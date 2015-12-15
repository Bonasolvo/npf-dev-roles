from django.conf import settings

XMIN_RECENT_ACTIONS = getattr(settings, "XMIN_RECENT_ACTIONS", 100)
XMIN_POLLING_INTERVAL = getattr(settings, "XMIN_POLLING_INTERVAL", 120000)

XMIN_XTYPE_FORMFIELD_MAP = {
    'django.forms.fields.TextField': 'textareafield',
    'django.forms.fields.CharField': 'textfield',
    'django.forms.fields.DateField': 'datefield',
    'django.forms.fields.TypedChoiceField': 'choices',
    'django.forms.models.ModelChoiceField': 'relatedfield',
    'django.forms.fields.IntegerField': 'numberfield',
    'django.forms.fields.BooleanField': 'checkboxfield',
    'npf.contrib.address.forms.AddressField': {'xtype': 'addressfield', 'url': '/fias/suggest_sbs/'},
    'fias.forms.AddressSelect2Field': {'xtype': 'addressfield', 'url': '/fias/suggest_sbs/'},
    'fias.forms.AddressWithHouseSelect2Field': {'xtype': 'addressfield', 'url': '/fias/suggest_house_sbs/'}
}

XMIN_XTYPE_MODELFIELD_MAP = {
    'django.db.models.TextField': 'textareafield',
    'django.db.models.fields.CharField': 'textfield',
    'django.db.models.fields.DateField': 'datefield',
    'django.db.models.fields.related.ForeignKey': 'relatedfield',
    'fias.fields.address.AddressField': {'xtype': 'addressfield', 'url': '/fias/suggest_sbs/'},
    'fias.fields.address_with_house.AddressWithHouseField': {'xtype': 'addressfield', 'url': '/fias/suggest_house_sbs/'}
}

XMIN_FILTER_MODELFIELD_MAP = {
    'django.db.models.fields.TextField': 'string',
    'django.db.models.fields.CharField': 'string',
    'django.db.models.fields.DateField': 'date',
    'django.db.models.fields.PositiveIntegerField': 'number',
    'django.db.models.fields.PositiveSmallIntegerField': 'number',
    'django.db.models.fields.DateTimeField': 'date',
    'django.db.models.fields.BooleanField': 'boolean',
    'fias.fields.address.AddressField': {'type': 'address', 'url': '/fias/suggest_sbs/'},
    'fias.fields.address_with_house.AddressWithHouseField': {'type': 'address', 'url': '/fias/suggest_house_sbs/'},
}

XMIN_CHANGELIST_SERIALIZER = 'changelist'
XMIN_ADMINFORM_SERIALIZER = 'adminform'
XMIN_INLINE_ADMINFORMS_SERIALIZER = 'inline-adminforms'

settings.SERIALIZATION_MODULES.update({
    XMIN_CHANGELIST_SERIALIZER: 'npf.core.xmin.serializers.changelist',
    XMIN_ADMINFORM_SERIALIZER: 'npf.core.xmin.serializers.adminform',
    XMIN_INLINE_ADMINFORMS_SERIALIZER: 'npf.core.xmin.serializers.inline_adminforms',
})
