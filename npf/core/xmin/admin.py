import json

from django.db import models, transaction
from django.db.models import CharField, ForeignKey
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, Http404
from django.utils.encoding import force_text, smart_text
from django.utils.translation import ugettext as _
from django.utils.html import escape
from django.contrib import admin
from django.contrib.admin.views.main import ALL_VAR
from django.contrib.admin.options import InlineModelAdmin, ModelAdmin
from django.contrib.admin.filters import SimpleListFilter, RelatedFieldListFilter, FieldListFilter
from django.contrib.admin.utils import unquote
from django.contrib.admin.views.main import PAGE_VAR, ORDER_VAR, SEARCH_VAR, ChangeList
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import UserAdmin, GroupAdmin, csrf_protect_m
from npf.contrib.userprofile.models import UserProfile

from npf.core.printform.create_doc import create_excel
from .settings import (
    XMIN_ADMINFORM_SERIALIZER,
    XMIN_INLINE_ADMINFORMS_SERIALIZER,
    XMIN_CHANGELIST_SERIALIZER,
    XMIN_FILTER_MODELFIELD_MAP)
from .util import json_serialize
from .views import ServerEvents


def getter_for_related_field(name, admin_order_field=None, short_description=None):
    """
        Create a function that can be attached to a ModelAdmin to use as a list_display field, e.g:
        client__name = getter_for_related_field('client__name', short_description='Client')
    """
    related_names = name.split('__')

    def getter(self, obj):
        for related_name in related_names:
            obj = getattr(obj, related_name) if obj else None
        return obj

    getter.admin_order_field = admin_order_field or name
    getter.short_description = short_description or related_names[-1].title().replace('_', ' ')
    return getter


class RelatedFieldAdminMixin(object):
    """
        Version of ModelAdmin that can use related fields in list_display, e.g.:
        list_display = ('address__city', 'address__country__country_code')
    """
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        list_display = self.list_display if isinstance(self, admin.ModelAdmin) else self.fields

        # include all related fields in queryset
        select_related = [field.rsplit('__', 1)[0] for field in list_display if '__' in field and field != '__str__']

        # Include all foreign key fields in queryset.
        # This is based on ChangeList.get_query_set().
        # We have to duplicate it here because select_related() only works once.
        # Can't just use list_select_related because we might have multiple__depth__fields it won't follow.
        model = qs.model
        for field_name in list_display:
            try:
                field = model._meta.get_field(field_name)
            except models.FieldDoesNotExist:
                continue

            if isinstance(field.rel, models.ManyToOneRel):
                select_related.append(field_name)

        return qs.select_related(*select_related)


class XminChangeList(ChangeList):

    def __init__(self, request, model, list_display, *args):
        """
        Parse Ext-generated params and convert them to Django Admin params
        """

        request.GET._mutable = True

        if '_dc' in request.GET:
            del request.GET['_dc']

        if 'inline' in request.GET:
            del request.GET['inline']

        # Paging
        page = request.GET.get('page', 0)
        if page:
            del request.GET['page']
            request.GET[PAGE_VAR] = int(page) - 1

        # Sorting
        sort = request.GET.get('sort')
        order = []
        if sort:
            sort = json.loads(sort)
            for sort_field in sort:
                try:
                    field_index = str(list_display.index(sort_field['property']))
                    if sort_field['direction'] == 'DESC':
                        field_index = '-' + field_index
                    order.append(field_index)
                except ValueError:
                    pass

            del request.GET['sort']
            request.GET[ORDER_VAR] = '.'.join(order)

        # Searching
        search = request.GET.get('q')
        if search:
            del request.GET['q']
            request.GET[SEARCH_VAR] = search

        # Filtering
        filter = request.GET.get('filter')
        if filter:
            del request.GET['filter']
            filter = json.loads(filter)
            for filter_field in filter:
                if filter_field['operator'] == 'like':
                    field_name = filter_field['property'] + '__icontains'
                elif filter_field['operator'] in ['gt', 'lt', 'gte', 'lte']:
                    field_name = filter_field['property'] + '__' + filter_field['operator']
                else:
                    field_name = filter_field['property']
                if 'value' in filter_field:
                    request.GET[field_name] = filter_field['value']
                else:
                    request.GET[field_name] = ''

        super().__init__(request, model, list_display, *args)


class GridColumnsMixin(object):

    columns = []

    def get_columns(self, request, obj=None):
        list_filter = self.get_list_filter(request)
        filters = {}

        for filter in list_filter:
            if callable(filter):
                filter = filter(request, {}, self.model, self)
                if isinstance(filter, SimpleListFilter):
                    filters[filter.parameter_name] = {'choices': [('all', 'Все')] + filter.lookup_choices}
            else:
                filters[filter] = {}

        if not self.columns:
            self.columns = [{'dataIndex': column} for column in self.get_list_display(request)]

        return self.__prepare_model_columns(self.model._meta, self.columns, filters)

    def __prepare_model_columns(self, opts, columns, filters):
        """
        Формирование метаданных использующихся для задания внешенего вида колонок,
        добавления фильтров и возможности сортировки
        """
        for column in columns:
            if 'dataIndex' in column:
                if 'width' in column and 'minWidth' not in column:
                    column['minWidth'] = column['width']

                if 'minWidth' not in column:
                    column['minWidth'] = 100

                try:
                    f = opts.get_field(column['dataIndex'])
                except models.FieldDoesNotExist:
                    if 'sortable' not in column:
                        column['sortable'] = False

                    if 'text' not in column:
                        if column['dataIndex'] == '__str__':
                            column['text'] = opts.verbose_name
                        else:
                            attr = getattr(self, column['dataIndex'], None)
                            if hasattr(attr, 'short_description'):
                                column['text'] = attr.short_description
                            if hasattr(attr, 'admin_order_field'):
                                column['sortable'] = True

                    # Инициализация фильтра по вычисляемым колонкам
                    if 'filter' not in column and column['dataIndex'] in filters:
                        filter = filters[column['dataIndex']]
                        if 'choices' in filter:
                            column['filter'] = {'type': 'choices', 'choices': filter['choices']}

                else:
                    if 'sortable' not in column:
                        column['sortable'] = True

                    # Инициализация заголовка колонки модели
                    if 'text' not in column:
                        column['text'] = force_text(f.verbose_name)

                    # Инициализация фильтра по колонкам модели
                    if 'filter' not in column and f.name in filters:
                        if isinstance(f, CharField) and f.choices:
                            column['filter'] = {'type': 'choices', 'choices': [('all', 'Все')] + list(f.choices)}
                        else:
                            class_name = '{0}.{1}'.format(f.__module__, f.__class__.__name__)
                            if class_name in XMIN_FILTER_MODELFIELD_MAP:
                                column['filter'] = XMIN_FILTER_MODELFIELD_MAP[class_name]
                            elif isinstance(f, ForeignKey):
                                column['filter'] = {'type': 'related', 'model': smart_text(f.rel.to._meta)}

            if 'columns' in column:
                self.__prepare_model_columns(opts, column['columns'], filters)
        return columns


class TabularInlineMixin(GridColumnsMixin, InlineModelAdmin, admin.ModelAdmin):

    commit_unchanged_records = False

    def __init__(self, parent_model, admin_site):
        self.admin_site = admin_site
        self.parent_model = parent_model
        self.opts = self.model._meta

        if self.verbose_name is None:
            self.verbose_name = self.model._meta.verbose_name
        if self.verbose_name_plural is None:
            self.verbose_name_plural = self.model._meta.verbose_name_plural

        super(ModelAdmin, self).__init__()


class XminStackedInline(admin.StackedInline):
    pass


class XminTabularInline(TabularInlineMixin, admin.TabularInline):
    pass


class XminGenericTabularInline(TabularInlineMixin, GenericTabularInline):
    pass


class XminAdmin(GridColumnsMixin, RelatedFieldAdminMixin, admin.ModelAdmin):
    """
    Базовый класс для админских моделей
    """
    list_max_show_all = 1000000

    def get_inline_instances(self, request, obj=None):
        inlines = super().get_inline_instances(request, obj)

        if request.method == 'POST':
            return inlines

        inline_class = request.GET.get('inline', False)

        # Request all inlines
        if not inline_class:
            return inlines

        # Request specific inline class
        for inline in inlines:
            if inline.__class__.__name__ == inline_class:
                if not isinstance(inline, (XminTabularInline, XminGenericTabularInline)):
                    raise ValueError(_('%(inline)s is not (TabularInline, GenericTabularInline) instance') %
                                     {'inline': inline_class})
                return [inline]

        raise Http404(_('%(inline)s not found.') % {'inline': inline_class})

    def get_changelist(self, request, **kwargs):
        return XminChangeList

    def suggest_items(self, model, suggest_context=None, object_id=None):
        return model.objects.all()

    def response_add(self, request, obj, post_url_continue=None):
        if not request.is_ajax():
            return super().response_add(request, obj, post_url_continue)

        response = {
            'success': True,
            'msg': _('Item saved'),
            'data': obj,
            'event': ServerEvents.get_latest_event_for(request.user, obj)
        }

        return HttpResponse(json_serialize(response))

    def response_change(self, request, obj):
        if not request.is_ajax():
            return super().response_change(request, obj)

        response = {
            'success': True,
            'msg': _('Item saved'),
            'data': obj,
            'event': ServerEvents.get_latest_event_for(request.user, obj)
        }

        return HttpResponse(json_serialize(response), content_type='application/json')

    @csrf_protect_m
    @transaction.atomic
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        """
        Сериализация и формирование ответа с запрашиваемой формой.
        """
        inline_class = request.GET.get('inline', None)

        if not inline_class or request.method == 'POST':
            return super().changeform_view(request, object_id, form_url, extra_context)

        model = self.model
        opts = model._meta
        add = object_id is None

        if add:
            if not self.has_add_permission(request):
                raise PermissionDenied
            obj = None

        else:
            obj = self.get_object(request, unquote(object_id))

            if not self.has_change_permission(request, obj):
                raise PermissionDenied

            if obj is None:
                raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {
                    'name': force_text(opts.verbose_name), 'key': escape(object_id)})

        if add:
            formsets, inline_instances = self._create_formsets(request, None, change=False)
        else:
            formsets, inline_instances = self._create_formsets(request, obj, change=True)

        inline_instance = inline_instances[0]
        formset = formsets[0]

        inline_instance.get_queryset = (lambda request: formset.queryset)

        list_display = inline_instance.get_fields(request, obj)
        list_display_links = inline_instance.get_list_display_links(request, list_display)
        list_filter = inline_instance.get_list_filter(request)
        search_fields = inline_instance.get_search_fields(request)
        list_editable = ()

        cl = XminChangeList(
            request, inline_instance.model, list_display, list_display_links, list_filter,
            inline_instance.date_hierarchy, search_fields, inline_instance.list_select_related,
            inline_instance.list_per_page, inline_instance.list_max_show_all, list_editable,
            inline_instance)

        response = HttpResponse(content_type='application/json')
        response.write('{')
        response.write('"success": true, ')
        response.write('"data":')

        changelist_serializer = serializers.get_serializer(XMIN_CHANGELIST_SERIALIZER)()
        changelist_serializer.serialize(cl, ensure_ascii=False, stream=response)

        response.write(', "total": {0}'.format(cl.result_count))
        response.write('}')

        return response

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        if not request.is_ajax():
            return super().render_change_form(request, context, add, change, form_url, obj)

        admin_form = context['adminform']
        inline_admin_formsets = context['inline_admin_formsets']
        errors = context['errors']

        if errors:
            data = {'success': False, 'errors': {}}
            data['errors'].update(self._adminform_errors_dict(admin_form))
            data['errors'].update(self._adminform_inline_errors_dict(inline_admin_formsets))
            return HttpResponse(content=json_serialize(data), content_type='application/json')

        adminform_serializer = serializers.get_serializer(XMIN_ADMINFORM_SERIALIZER)()

        inline_adminforms_serializer = serializers.get_serializer(XMIN_INLINE_ADMINFORMS_SERIALIZER)()

        response = HttpResponse(content_type='application/json')
        response.write('{')
        response.write('"success": true, ')
        response.write('"perms": {')
        response.write('"add": {0},'.format('true' if self.has_add_permission(request) else 'false'))
        response.write('"change": {0},'.format('true' if self.has_change_permission(request, obj) else 'false'))
        response.write('"delete": {0}'.format('true' if self.has_delete_permission(request, obj) and not add
                                              else 'false'))
        response.write('}, ')
        response.write('"adminform":')

        adminform_serializer.serialize(context['adminform'], ensure_ascii=False, stream=response)

        response.write(', ')
        response.write('"adminform_inline":')

        inline_adminforms_serializer.serialize(context['inline_admin_formsets'], request=request, ensure_ascii=False,
                                               stream=response)

        response.write('}')
        return response

    @csrf_protect_m
    def changelist_view(self, request, extra_context=None, module_name=None):
        """
        Сериализация списка объектов и формирование JSON ответа.
        В случае, если был передан параметр 'export', формирует и возвращает exel файл.
        """

        if not request.is_ajax() and not request.GET.get('export'):
            return super().changelist_view(request, extra_context)

        # check export
        export = request.GET.get('export')
        if export:
            json_string = request.POST.get('values').replace('&quot;', '"')
            values = json.loads(json_string)
            export_columns = values['columns']
            excel_heading = values['excel_heading']

            request.GET._mutable = True
            request.GET[ALL_VAR] = 'true'
            del request.GET['export']

        template = self.change_list_template
        self.change_list_template = 'change_list.html'
        context = super().changelist_view(request, extra_context).context_data

        response = HttpResponse(content_type='application/json')
        response.write('{')
        response.write('"success": true, ')
        response.write('"perms": {')
        response.write('"add": {0}'.format('true' if context['has_add_permission'] else 'false'))
        response.write('}, ')
        response.write('"data":')

        changelist_serializer = serializers.get_serializer(XMIN_CHANGELIST_SERIALIZER)()

        changelist_serializer.serialize(context['cl'], ensure_ascii=False, stream=response)

        response.write(', "total": {0}'.format(context['cl'].result_count))
        response.write('}')

        self.change_list_template = template

        """
        Формирование exel файла
        """
        if export:
            decoded_resp = json.loads(response.serialize().decode("utf-8").replace('Content-Type: application/json\r\n\r\n', ''))
            if decoded_resp['data']:
                response = create_excel(decoded_resp, module_name, export_columns, excel_heading)
                return response
            else:
                return HttpResponse({})

        return response

    def _adminform_errors_dict(self, admin_form):
        return admin_form.form.errors.as_data()

    def _adminform_inline_errors_dict(self, inline_admin_formsets):
        for inline_admin_formset in inline_admin_formsets:
            if not inline_admin_formset.formset.errors:
                continue
            for form in inline_admin_formset.formset.forms:
                if not form.errors:
                    continue
                for error in form.errors:
                    yield ('{0}-{1}'.format(form.prefix, error), list(form.errors[error]))


class UserExtAdmin(XminAdmin, UserAdmin):
    pass


class GroupExtAdmin(XminAdmin, GroupAdmin):
    pass


class ExtAdminTreeMixin():
    def is_tree(self):
        pass


class LazyRelatedFieldListFilter(RelatedFieldListFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        # Prevent hit database query in RelatedFieldListFilter
        field.get_choices = (lambda include_blank=False: [])
        super().__init__(field, request, params, model, model_admin, field_path)


admin.site.unregister([Group])
admin.site.register(User, UserExtAdmin)
admin.site.register(Group, GroupExtAdmin)


FieldListFilter.register(lambda f: (
    bool(f.rel) if hasattr(f, 'rel') else
    isinstance(f, models.related.RelatedObject)), LazyRelatedFieldListFilter, take_priority=True)
