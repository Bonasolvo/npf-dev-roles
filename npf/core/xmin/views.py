import json
import random
import urllib
import operator
from io import BytesIO
from zipfile import ZipFile
from functools import reduce

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.models import LogEntry
from django.contrib.admin.utils import unquote
from django.contrib.admin.views.main import SEARCH_VAR
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage
from django.db.models import BLANK_CHOICE_DASH, Q
from django.http import HttpResponse, Http404, HttpResponseBadRequest, QueryDict, JsonResponse
from django.shortcuts import render_to_response
from django.utils.html import escape
from django.utils.translation import ugettext as _
from django.utils.encoding import force_text, smart_text
from django.views.generic import View
from django.core import urlresolvers
from django.contrib.auth.models import User
from django.template import Context, Template

from .settings import XMIN_RECENT_ACTIONS, XMIN_POLLING_INTERVAL
from .util import json_serialize
from .util.admin import get_app_list, get_model_and_admin_or_404, get_actions
from npf.core.printform.create_doc import CreateDoc


class JsonPrettyMixin(object):
    def convert_context_to_json(self, context):
        return json.dumps(context, ensure_ascii=False)


class StartXmin(View):

    def get(self, request, *args, **kwargs):
        """
        Initialize application
        """
        if not admin.site.has_permission(request):
            raise PermissionDenied

        xmin_settings = {
            'site_title': admin.site.site_title,
            'urls': {
                'logout': urlresolvers.reverse('admin:logout'),
                'password_change': urlresolvers.reverse('admin:password_change'),
                'xmin_data': urlresolvers.reverse('xmin-data'),
            },
            'app_list': get_app_list(request),
            'poll_interval': XMIN_POLLING_INTERVAL,
            'user': {
                'name': request.user.get_full_name() or request.user.username,
                'id': request.user.id,
            }
        }

        context = {
            'settings': json_serialize(xmin_settings),
        }

        return render_to_response('xmin_start.html', context)


class ChangeList(View):

    def get(self, request, app_label, module_name, action=None):
        """
        Returns a list of items defined in the database for the specified model (module) and app
        Paging, Sorting and Search parameters are passed as GET values.
        """

        self.init(request, app_label, module_name)

        # @TODO: Check permissions

        '''
        # Tree or grid
        node = request.GET.get('node')
        if node:
            response = self.get_tree_result(request, node)
        else:
            change_list = self.get_change_list(request, max_show_all)
            response = {
                'totalCount': change_list.result_count,
                'data': change_list.result_list
            }
        '''

        # @TODO: Populate dynamic values into change_list.result_list,
        # such as __str__ from list_display
        return self.model_admin.changelist_view(request, None, module_name=module_name)

    def post(self, request, app_label, module_name, action=None):
        """
        1. Добавление записи в таблицу
        2. Массовое удаление записей (с выделенным checkbox)
        3. Экспорт списка в excel
        """
        self.init(request, app_label, module_name)

        if not action:
            if request.GET.get('export'):
                return self.model_admin.changelist_view(request, None, module_name=module_name)
            return HttpResponseBadRequest()
        elif action == 'add':
            return self.add_item(request)
        elif action == 'bulk_update':
            return self.bulk_update(request)

    def init(self, request, app_label, module_name):
        (self.app_label, self.module_name) = (app_label, module_name)
        (self.model, self.model_admin) = get_model_and_admin_or_404(app_label, module_name)
        self.token = request.path[len(urlresolvers.reverse('xmin-data')) - 1:]

    def get_change_list(self, request):
        (model, model_admin) = (self.model, self.model_admin)

        list_display = model_admin.get_list_display(request)
        list_display_links = model_admin.get_list_display_links(request, list_display)

        ChangeList = model_admin.get_changelist(request)
        return ChangeList(
            request, model_admin.model, list_display,
            list_display_links, model_admin.list_filter, model_admin.date_hierarchy,
            model_admin.search_fields, model_admin.list_select_related,
            model_admin.list_per_page, model_admin.list_max_show_all, model_admin.list_editable,
            model_admin)

    def get_tree_result(self, request, node):
        """
        Рендер древовидного предстваления
        """
        def _make_query(list_display, search):
            pattern = 'Q({FIELD}__icontains="{SEARCH}")'
            first = True
            result = ''
            for item in list_display:
                if not first:
                    result += ' | '
                first = False
                result += pattern.format(FIELD=item, SEARCH=search)
            return eval(result)

        def _prepare_result(items, list_display, put_leaves=False):
            result = []
            for item in items:
                item_result = {}
                for field in list_display:
                    item_result[field] = getattr(item, field)
                item_result['id'] = item.id
                if not item.get_children() or put_leaves:
                    item_result['leaf'] = True
                result.append(item_result)
            return result

        def _find_items(list_display, search):
            query = _make_query(list_display, search)
            return self.model.objects.filter(query)

        list_display = self.model_admin.get_list_display(request)
        search = request.GET.get(SEARCH_VAR)

        if search:
            items = _find_items(list_display, search)
            result = _prepare_result(items, list_display, put_leaves=True)
        else:
            if node == 'root':
                items = self.model.objects.filter(level=0)
            else:
                items = self.model.objects.get(id=node).get_children()
            result = _prepare_result(items, list_display)

        return result

    def add_item(self, request):
        """
        CREATE - Add a new object based on values from form.
        """
        return self.model_admin.change_view(request)

    def bulk_update(self, request):
        if not self.model_admin.has_change_permission(request):
            raise PermissionDenied

        change_list = self.get_change_list(request)
        self.model_admin.delete_selected_confirmation_template = 'delete_selected_confirmation.html'
        action_response = self.model_admin.response_action(
            request,
            queryset=change_list.get_queryset(request))
        self.model_admin.delete_selected_confirmation_template = None

        # FIXME delete action don't saved in entry log
        if action_response and action_response.status_code == 302:
            response = {'success': True}
            return HttpResponse(json_serialize(response))

        if action_response and action_response.status_code == 200:
            response = {
                'success': True,
                'confirmation': action_response.render().content.strip()
            }
            return HttpResponse(json_serialize(response))

        messages.error(request, _("Action failed to complete..."))
        return HttpResponseBadRequest()


class ChoiceList(View):

    def get(self, request):
        """
        Рендер списка для поля select
        """
        app = request.GET.get('app', None)
        model = request.GET.get('model', None)
        field = request.GET.get('field', None)
        limit = request.GET.get('limit', 25)
        page = request.GET.get('page', 1)

        if not (app and model and field) or int(limit) > 100:
            return HttpResponseBadRequest()

        # @TODO: Check permissions

        content_type = ContentType.objects.get_by_natural_key(app, model)
        model_class = content_type.model_class()
        field = model_class._meta.get_field_by_name(field)[0]

        queryset = field.rel.to._default_manager.all()
        p = Paginator(queryset, limit)

        first_choice = BLANK_CHOICE_DASH if int(page) == 1 else []

        lst = [(x._get_pk_val(), smart_text(x)) for x in p.page(page).object_list]

        response = {
            'success': True,
            'data': first_choice + lst,
            'total': queryset.count()
        }

        return HttpResponse(json_serialize(response))


class ItemRestApi(View):
    def init(self, request, app_label, module_name, object_id):
        self.model, self.model_admin = get_model_and_admin_or_404(app_label, module_name)

        self.opts = self.model._meta
        self.object = self.model_admin.get_object(request, unquote(object_id))

        if self.object is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') %
                          {'name': force_text(self.opts.verbose_name), 'key': escape(object_id)})

    def get(self, request, app_label, module_name, object_id=None):
        """
        READ - Retrieve the object data in order to fill in the edit form.
        """
        # self.init(request, app_label, module_name, object_id)
        self.model, self.model_admin = get_model_and_admin_or_404(app_label, module_name)

        # check suggest items
        suggest_context = request.GET.get('suggest_context')
        if suggest_context:
            return self._get_suggest_items(request, app_label, module_name, suggest_context, object_id)

        # check create doc
        create_doc = request.GET.get('create_doc')
        if create_doc:
            return self._create_doc(request)

        return self.model_admin.change_view(request, object_id)

    def post(self, request, app_label, module_name, object_id=None):
        """
        UPDATE - Save edit form values to update an existing object.
        """
        self.model, self.model_admin = get_model_and_admin_or_404(app_label, module_name)
        # check upload
        request = self._check_upload(request, object_id)
        return self.model_admin.change_view(request, object_id)

    def delete(self, request, app_label, module_name, object_id):
        """
        DELETE - Delete an existing object.
        """
        (self.model, self.model_admin) = get_model_and_admin_or_404(app_label, module_name)

        request.POST = QueryDict(request.body.decode('utf-8'))

        self.model_admin.delete_confirmation_template = 'delete_confirmation.html'
        delete_response = self.model_admin.delete_view(request, object_id)

        if delete_response and delete_response.status_code == 302:
            response = {
                'success': True,
                'event': ServerEvents.get_latest_event_for(request.user, object_id, self.model)
            }
            return HttpResponse(json_serialize(response))

        if delete_response and delete_response.status_code == 200:
            response = {
                'success': True,
                'confirmation': delete_response.rendered_content.strip()
            }
            return HttpResponse(json_serialize(response))

        messages.error(request, _("Action failed to complete..."))
        return HttpResponseBadRequest()

    def _check_upload(self, request, object_id):
        if request.FILES:
            for key in request.FILES.keys():
                file = request.FILES[key]
                request.POST[key] = file
        return request

    def _get_suggest_items(self, request, app_label, module_name, suggest_context, object_id):
        """
        Динамическая подгрузка объектов для указанной модели и контекста (пр.: select поля формы)
        """
        term = request.GET.get('term', None)
        page = int(request.GET.get('page', None))
        model = request.GET.get('model').split('.')
        context_model, admin_model = get_model_and_admin_or_404(app_label, module_name)

        queryset = admin_model.suggest_items(model, suggest_context, object_id)
        if admin_model.ordering:
            for field in admin_model.ordering:
                queryset = queryset.order_by(field)

        if term:
            or_queries = []

            for field in admin_model.search_fields:
                or_queries.append(Q(("%s__icontains" % field, term)))

            if or_queries:
                queryset = queryset.filter(reduce(operator.or_, or_queries))

        p = Paginator(queryset, 100)

        try:
            data = list([(obj._get_pk_val(), smart_text(obj)) for obj in p.page(page).object_list])
        except EmptyPage:
            data = []

        result = {
            'data': data,
            'total': p.count
        }

        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=DjangoJSONEncoder),
                            content_type='application/json')

    def _create_doc(self, request):
        """
        Обработка запроса на формирование печатной формы
        """
        doc = CreateDoc(request, self.model, self.model_admin)
        files = doc.run()
        if len(files) == 1:
            # если файл 1, то отдаем его в исходном виде
            for filename, file in files.items():
                pass
            file_path = file
            tmptmp = urllib.parse.quote_plus(filename).replace('+', '_') + '.docx'

            zp = self._render_to_docx(file_path, {})
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            response['Content-Disposition'] = "attachment; filename*=UTF-8''{}".format(tmptmp)
            response.write(zp.getvalue())
            return response
        if len(files) > 1:
            # если файлов много, архивируем и отдаем архив
            zip_name = 'docs_' + str(random.randint(0, 10000)) + '.zip'
            tmp = BytesIO()
            zipf = ZipFile(tmp, 'w')
            for file_name, file in files.items():
                file_path = file
                zipf.write(file_path, file_name + '.docx')
            zipf.close()
            response = HttpResponse(tmp.getvalue(), content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename={}'.format(zip_name)
            return response

    def _render_to_docx(self, docx, context):
        tmp = BytesIO()
        with ZipFile(tmp, 'w') as document_zip, ZipFile(docx) as template_zip:
            template_archive = {name: template_zip.read(name) for name in template_zip.namelist()}
            template_xml = template_archive.pop('word/document.xml')
            for n, f in template_archive.items():
                document_zip.writestr(n, f)
            t = Template(template_xml)
            document_zip.writestr('word/document.xml', t.render(Context(context)))
        return tmp


class ServerEvents(View):
    """
    События, которые совершает пользователь.
    Используется для формирования журнала действий пользователя.
    """
    def get(self, request, event_id):
        events = []
        last_event_id = 0

        if event_id == 'recent':
            log_entries = LogEntry.objects.order_by('-pk')[:XMIN_RECENT_ACTIONS]
        else:
            last_event_id = int(event_id)
            log_entries = LogEntry.objects.order_by('-pk').filter(pk__gt=event_id)

        current_user = request.user.username

        for entry in log_entries:
            entry_user = entry.user.get_full_name() or entry.user.username
            if not current_user == entry_user:
                continue
            events.insert(0, ServerEvents.make_event(entry))

        if len(log_entries):
            last_event = log_entries[0]
            last_event_id = last_event.id

        response = {
            'success': True,
            'events': events,
            'last_id': last_event_id
        }

        return HttpResponse(json_serialize(response))

    @staticmethod
    def make_event(log_entry):

        try:
            edited_object = log_entry.get_edited_object()
        except ObjectDoesNotExist:
            edited_object = None
        except AttributeError:
            edited_object = None

        def _process_datetime(raw):
            raw = str(raw)
            raw = raw.split('.')[0]
            raw = raw.replace('T', ' ')
            return raw

        event = {
            'id': log_entry.id,
            'app': log_entry.content_type.app_label,
            'model': log_entry.content_type.model,
            'model_name': force_text(log_entry.content_type),
            'object_id': log_entry.object_id,
            'object': edited_object,
            'object_name': log_entry.object_repr,
            'user_id': log_entry.user_id,
            'user_name': log_entry.user.get_full_name() or log_entry.user.username,
            'token': log_entry.get_admin_url(),
            'action': {1: 'ADDITION', 2: 'CHANGE', 3: 'DELETION'}[log_entry.action_flag],
            'message': log_entry.change_message,
            'datetime': _process_datetime(log_entry.action_time),
            'leaf': True,
            'record_id': log_entry.object_id,
            'text': log_entry.object_repr
        }
        return event

    @staticmethod
    def get_latest_event_for(user, item_or_id, model=None):
        object_id = item_or_id.id if isinstance(item_or_id, models.Model) else item_or_id
        content_type_id = ContentType.objects.get_for_model(model or item_or_id, for_concrete_model=False).id

        log_entry = LogEntry.objects.filter(
            user=user,
            object_id=object_id,
            content_type__id__exact=content_type_id
        ).select_related().order_by('-pk')[:1][0]

        return ServerEvents.make_event(log_entry)


def password_change_custom(request):
    def _set_password():
        user = User.objects.get(username__exact=request.user.username)
        user.set_password(data['new_password'])
        user.save()

    def _check_old_password():
        return request.user.check_password(data['old_password'])

    def _check_new_passwords():
        return data['new_password'] == data['new_password_again']

    result = {
        'errors': {},
    }
    data = json.loads(request.body.decode('utf-8'))

    if not _check_old_password():
        result['errors']['incorrect'] = True
    if not _check_new_passwords():
        result['errors']['missmatch'] = True

    if not result['errors']:
        _set_password()
        result['success'] = True
    else:
        result['success'] = False

    return HttpResponse(json.dumps(result), content_type='application/json')


class SuggestItems(View):
    """
    Базовое представление для динамической подгрузки списочных данных.
    Используется, если для списка явно не указана ссылка на метод и контекст для получения данных.
    """
    def get(self, request):
        term = request.GET.get('term', None)
        page = int(request.GET.get('page', None))
        app_name, model_name = request.GET.get('model').split('.')
        model, admin_model = get_model_and_admin_or_404(app_name, model_name)

        queryset = admin_model.suggest_items(model)
        if admin_model.ordering:
            for field in admin_model.ordering:
                queryset = queryset.order_by(field)

        if term:
            or_queries = []

            for field in admin_model.search_fields:
                or_queries.append(Q(("%s__icontains" % field, term)))

            if or_queries:
                queryset = queryset.filter(reduce(operator.or_, or_queries))

        p = Paginator(queryset, 100)

        try:
            data = list([(obj._get_pk_val(), smart_text(obj)) for obj in p.page(page).object_list])
        except EmptyPage:
            data = []

        result = {
            'data': data,
            'total': p.count
        }

        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=DjangoJSONEncoder),
                            content_type='application/json')


def action_list(request, app_label, module_name):
    model, model_admin = get_model_and_admin_or_404(app_label, module_name)
    return JsonResponse(get_actions(request, model, model_admin), safe=False)
