from __future__ import absolute_import
from __future__ import unicode_literals

from django.db.models.fields.files import FieldFile
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.admin.helpers import AdminField, AdminReadonlyField
from django.forms import TypedChoiceField, ModelChoiceField
from django.utils.encoding import smart_text
from django.utils.functional import Promise
from django.forms.models import ModelChoiceIterator


class DjangoAdminJSONEncoder(DjangoJSONEncoder):

    def default(self, o):
        if isinstance(o, Promise):
            return str(o)
        if issubclass(o.__class__, ModelChoiceIterator):
            return []
        if isinstance(o, AdminReadonlyField):
            f = o.field
            return {
                'class': '{0}.{1}'.format(o.__class__.__module__, o.__class__.__name__),
                'help_text': str(f['help_text']),
                'editable': False,
                'verbose_name': str(f['label']),
            }
        if isinstance(o, AdminField):
            f = o.field.field
            field = {
                'class': '{0}.{1}'.format(f.__class__.__module__, f.__class__.__name__),
                'widget': '{0}.{1}'.format(f.widget.__class__.__module__, f.widget.__class__.__name__),
                'help_text': str(f.help_text),
                'editable': True,
                'allow_blank': not f.required,
                'verbose_name': str(f.label),
            }
            if hasattr(f, 'choices'):
                if isinstance(f, TypedChoiceField):
                    field['choices'] = f.choices
                elif isinstance(f, ModelChoiceField):
                    field['model'] = smart_text(f.queryset.model._meta)
                    if 'suggest_url' in f.widget.attrs:
                        field['suggest_url'] = f.widget.attrs['suggest_url']
            if hasattr(f, 'max_length'):
                field['max_length'] = f.max_length
            return field
        if isinstance(o, FieldFile):
            return str(o)
        return super().default(o)