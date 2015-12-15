import json

from django.db import models
from django.contrib.admin.utils import lookup_field, display_for_value, display_for_field
from django.contrib.admin.views.main import ChangeList, EMPTY_CHANGELIST_VALUE
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import Serializer as JSONSerializer
from django.utils import six
from django.utils.encoding import smart_text, force_text
from django.utils.safestring import mark_safe

from .json import DjangoAdminJSONEncoder


class Serializer(JSONSerializer):

    def serialize(self, changelist, **options):
        """
        Сериализация табличного представления.
        Пример выходных данных для таблицы сокращений:
        {
            "data":[
                {
                    "level": "0",
                    "item_weight": "64",
                    "socrname": "",
                    "scname": " ",
                    "id": 0
                },
                {
                    "level": "1",
                    "item_weight": "64",
                    "socrname": "Автономный округ",
                    "scname": "АО",
                    "id": 101
                }
            ]
        }
        """
        if not isinstance(changelist, ChangeList):
            raise TypeError('\'{0}\' is not {1} instance'.format(changelist, ChangeList))

        self.options = options
        self.changelist = changelist

        self.stream = options.pop("stream", six.StringIO())
        self.selected_fields = options.pop("fields", None)
        self.use_natural_keys = options.pop("use_natural_keys", False)
        self.use_natural_foreign_keys = options.pop('use_natural_foreign_keys', False) or self.use_natural_keys
        self.use_natural_primary_keys = options.pop('use_natural_primary_keys', False)

        self.start_serialization()
        self.first = True

        # для каждой записи в таблице
        for obj in self.changelist.result_list:
            self.start_object(obj)

            # для каждого поля в записи
            for field_name in self.changelist.list_display:
                if field_name == 'action_checkbox':
                    continue

                # получаем представление поля
                try:
                    f, attr, value = lookup_field(field_name, obj, self.changelist.model_admin)
                except ObjectDoesNotExist:
                    result_repr = EMPTY_CHANGELIST_VALUE
                else:
                    if f is None:
                        result_repr = display_for_value(value, False)
                    else:
                        if isinstance(f.rel, models.ManyToOneRel):
                            field_val = getattr(obj, f.name)
                            if field_val is None:
                                result_repr = EMPTY_CHANGELIST_VALUE
                            else:
                                result_repr = field_val
                        else:
                            result_repr = display_for_field(value, f)

                self._current[field_name] = mark_safe(force_text(result_repr))

            self.end_object(obj)
            if self.first:
                self.first = False
        self.end_serialization()
        return self.getvalue()

    def end_object(self, obj):
        # self._current has the field data
        indent = self.options.get("indent")
        if not self.first:
            # добавляем разделитель перед каждым полем кроме первого
            self.stream.write(",")
            if not indent:
                self.stream.write(" ")
        if indent:
            self.stream.write("\n")
        # записываем в поток набор сериализованных данных для табличного представления
        json.dump(self.get_dump_object(obj), self.stream,
                  cls=DjangoAdminJSONEncoder, **self.json_kwargs)
        self._current = None

    def get_dump_object(self, obj):
        if not self.use_natural_primary_keys or not hasattr(obj, 'natural_key'):
            self._current['id'] = smart_text(obj._get_pk_val(), strings_only=True)
        return self._current


Deserializer = None