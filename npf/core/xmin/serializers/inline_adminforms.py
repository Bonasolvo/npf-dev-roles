import json
from collections import OrderedDict

from django.utils import six
from django.forms import ModelChoiceField, ModelMultipleChoiceField, TypedChoiceField, FileField
from django.contrib import admin
from django.contrib.admin.helpers import AdminReadonlyField, InlineAdminFormSet
from django.core.serializers.json import Serializer as JSONSerializer
from django.utils.encoding import smart_text

from .json import DjangoAdminJSONEncoder
from ..admin import XminTabularInline, XminGenericTabularInline


class Serializer(JSONSerializer):
    def serialize(self, inline_admin_formsets, **options):
        """
        Сериализация админской инлайн-формы
        """
        self.options = options
        self.request = options.pop("request")
        self.stream = options.pop("stream", six.StringIO())

        self.start_serialization()
        self.first = True

        for obj in inline_admin_formsets:
            self.start_object(obj)
            self.end_object(obj)

            if self.first:
                self.first = False

        self.end_serialization()
        return self.getvalue()

    def end_object(self, obj):
        # self._current has the field data
        indent = self.options.get("indent")
        if not self.first:
            # добавляем разделитель перед каждым объектом кроме первого
            self.stream.write(",")
            if not indent:
                self.stream.write(" ")
        if indent:
            self.stream.write("\n")
        # записываем в поток набор сериализованных данных формы
        json.dump(self.get_dump_object(obj), self.stream,
                  cls=DjangoAdminJSONEncoder, **self.json_kwargs)
        self._current = None

    def get_dump_object(self, obj):
        if not isinstance(obj, InlineAdminFormSet):
            raise TypeError('\'{0}\' is not {1} instance'.format(obj, InlineAdminFormSet))

        fields = OrderedDict()
        inlines = list(obj)
        len_inlines = len(inlines)

        # формируем набор полей формы
        for inline in inlines:
            for fieldset in inline:
                for line in fieldset:
                    for field in line:
                        if isinstance(field, AdminReadonlyField):
                            fields[field.field['name']] = field
                        else:
                            fields[field.field.name] = field
                break
            break

        data = OrderedDict({
            'class': obj.opts.__class__.__name__,
            'verbose_name_plural': obj.opts.verbose_name_plural,
            'prefix': obj.formset.prefix,
            'model': smart_text(obj.formset.form._meta.model._meta),
            'fields': fields,
            'management_form': obj.formset.management_form.initial,
            'hidden_fields': [],
            'data': [],
            'perms': {
                'add': obj.opts.has_add_permission(self.request),
                'delete': obj.opts.has_delete_permission(self.request)
            }
        })

        if isinstance(obj.opts, admin.StackedInline):
            data['fieldsets'] = obj.fieldsets
        else:
            data['commit_unchanged_records'] = False

        if isinstance(obj.opts, (XminTabularInline, XminGenericTabularInline)):
            # данные для правильного отображения заголовков таблицы
            data['columns'] = obj.opts.get_columns(self.request, obj.formset.instance)
            data['commit_unchanged_records'] = obj.opts.commit_unchanged_records

        for index, inline in enumerate(inlines):
            if index == len_inlines - 1:
                break

            row = {}
            prefix = '{0}-{1}'.format(obj.formset.prefix, index) if isinstance(obj.opts, admin.StackedInline) else ''

            if inline.needs_explicit_pk_field():
                pk_field = inline.pk_field().field
                if pk_field.name not in data['hidden_fields']:
                    data['hidden_fields'].append(pk_field.name)

                field_name = pk_field.name
                field_name = '{0}-{1}'.format(prefix, field_name) if prefix else field_name
                row[field_name] = pk_field.value()

            try:
                fk_field = inline.fk_field().field
                if fk_field.name not in data['hidden_fields']:
                    data['hidden_fields'].append(fk_field.name)

                field_name = fk_field.name
                field_name = '{0}-{1}'.format(prefix, field_name) if prefix else field_name
                row[field_name] = fk_field.value()

            except AttributeError:
                pass

            for fieldset in inline:
                for line in fieldset:
                    for field in line:
                        name = getattr(field.field, 'name', None) or field.field['name']
                        field_name = '{0}-{1}'.format(prefix, name) if prefix else name

                        if isinstance(field, AdminReadonlyField):
                            row[field_name] = str(field.contents())
                        else:
                            row[field_name] = field.field.value()
                            if isinstance(field.field.field, FileField):
                                fname = getattr(field.field, 'name', None) or field.field['name']
                                url = getattr(inline.form.instance, fname)
                                try:
                                    row['{0}_url'.format(field_name)] = url.url
                                except Exception:
                                    row['{0}_url'.format(field_name)] = None
                            elif isinstance(field.field.field, TypedChoiceField):
                                display = getattr(inline.form.instance, 'get_{0}_display'.format(name))()
                                row['{0}_display'.format(field_name)] = display
                            elif isinstance(field.field.field, ModelMultipleChoiceField):
                                pass
                            elif isinstance(field.field.field, ModelChoiceField):
                                val = getattr(inline.form.instance, field.field.name, None)
                                if val.__class__.__name__ != 'ManyRelatedManager':
                                    row['{0}_display'.format(field_name)] = str(val) if val else None

            data['data'].append(row)

        return data

    def handle_field(self, obj, field):
        pass

    def handle_fk_field(self, obj, field):
        pass

    def handle_m2m_field(self, obj, field):
        pass


Deserializer = None
