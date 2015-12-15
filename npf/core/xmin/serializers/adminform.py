import json
from collections import OrderedDict

from django.utils import six
from django.forms import ModelChoiceField, ModelMultipleChoiceField, TypedChoiceField, FileField
from django.contrib.admin.helpers import AdminForm, AdminReadonlyField
from django.core.serializers.json import Serializer as JSONSerializer
from django.utils.encoding import smart_text
from django.contrib.auth.models import Permission, Group

from .json import DjangoAdminJSONEncoder


class Serializer(JSONSerializer):

    def start_serialization(self):
        if json.__version__.split('.') >= ['2', '1', '3']:
            # Use JS strings to represent Python Decimal instances (ticket #16850)
            self.options.update({'use_decimal': False})
        self._current = None
        self.json_kwargs = self.options.copy()
        self.json_kwargs.pop('stream', None)
        self.json_kwargs.pop('fields', None)
        if self.options.get('indent'):
            # Prevent trailing spaces
            self.json_kwargs['separators'] = (',', ': ')

    def end_serialization(self):
        if self.options.get("indent"):
            self.stream.write("\n")

        if self.options.get("indent"):
            self.stream.write("\n")

    def serialize(self, adminform, **options):
        """
        Сериализация админской формы.
        Пример выходных данных для формы адресных сокращений:
        {
            "adminform": {
                "fieldsets": [[null, {
                    "fields": [
                        "scname",
                        "socrname",
                        "level",
                        "item_weight"
                    ]}
                ]],
                "data": {
                    "scname": " ",
                    "item_weight": 64,
                    "socrname": "",
                    "level": "0"
                },
                "fields": {
                    "scname": {
                        "editable": false,
                        "help_text": "",
                        "class": "django.contrib.admin.helpers.AdminReadonlyField",
                        "verbose_name": "scname"
                    },
                    "socrname": {
                        "editable": false,
                        "help_text": "",
                        "class": "django.contrib.admin.helpers.AdminReadonlyField",
                        "verbose_name": "socrname"
                    },
                    "level": {
                        "editable": false,
                        "help_text": "",
                        "class": "django.contrib.admin.helpers.AdminReadonlyField",
                        "verbose_name": "уровень"
                    },
                    "item_weight": {
                        "editable": true,
                        "help_text": "",
                        "class": "django.forms.fields.IntegerField",
                        "verbose_name": "Item weight",
                        "widget": "django.contrib.admin.widgets.AdminIntegerFieldWidget",
                        "allow_blank": false
                    }
                },
                "verbose_name": "Сокращениие наименования адресного объекта",
                "__str__": "Добавить",
                "model": "address.socr"
            }
        }
        """
        if not isinstance(adminform, AdminForm):
            raise TypeError('\'{0}\' is not {1} instance'.format(adminform, AdminForm))

        self.adminform = adminform
        self.options = options

        self.stream = options.pop("stream", six.StringIO())

        self.start_serialization()
        self.first = True

        self.start_object(adminform)
        self.end_object(adminform)

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
        if not isinstance(obj, AdminForm):
            raise TypeError('\'{0}\' is not {1} instance'.format(obj, AdminForm))

        fields = OrderedDict()

        # формируем набор полей формы
        for fieldset in obj:
            for line in fieldset:
                for field in line:
                    if isinstance(field, AdminReadonlyField):
                        fields[field.field['name']] = field
                    else:
                        fields[field.field.name] = field

        data = OrderedDict({
            '__str__': 'Добавить' if not obj.form.instance.pk else str(obj.form.instance),
            'verbose_name': obj.model_admin.opts.verbose_name,
            'model': smart_text(obj.form._meta.model._meta),
            'fields': fields,
            'fieldsets': obj.fieldsets,
            'data': {}
        })

        for fieldset in obj:
            for line in fieldset:
                for field in line:
                    """
                    Заполнение дополнительных данных для полей формы.
                    Для каждого типа поля сериализуются свои данные.
                    """
                    field_name = getattr(field.field, 'name', None) or field.field['name']

                    if isinstance(field, AdminReadonlyField):
                        data['data'][field_name] = str(field.contents())
                    else:
                        data['data'][field_name] = field.field.value()
                        if isinstance(field.field.field, FileField):
                            fname = getattr(field.field, 'name', None) or field.field['name']
                            url = getattr(obj.form.instance, fname)
                            try:
                                data['data']['{0}_url'.format(field_name)] = url.url
                            except Exception:
                                data['data']['{0}_url'.format(field_name)] = None
                        elif isinstance(field.field.field, TypedChoiceField):
                            display = getattr(obj.form.instance, 'get_{0}_display'.format(field_name))()
                            data['data']['{0}_display'.format(field_name)] = display
                        if isinstance(field.field.field, ModelMultipleChoiceField):
                            if field_name == 'user_permissions':
                                data['data']['user_permissions'] = {
                                    'user': data['data']['user_permissions'],
                                    'all': [[i.id, i.__str__()] for i in Permission.objects.all()]
                                }
                            if field_name == 'groups':
                                data['data']['groups'] = {
                                    'user': data['data']['groups'],
                                    'all': [[i.id, i.__str__()] for i in Group.objects.all()]
                                }
                            if field_name == 'permissions':
                                data['data']['permissions'] = {
                                    'user': data['data']['permissions'],
                                    'all': [[i.id, i.__str__()] for i in Permission.objects.all()]
                                }
                        elif isinstance(field.field.field, ModelChoiceField):
                            val = getattr(obj.form.instance, field.field.name, None)
                            if val.__class__.__name__ != 'ManyRelatedManager':
                                data['data']['{0}_display'.format(field_name)] = str(val) if val else None

        return data

    def handle_field(self, obj, field):
        pass

    def handle_fk_field(self, obj, field):
        pass

    def handle_m2m_field(self, obj, field):
        pass

Deserializer = None