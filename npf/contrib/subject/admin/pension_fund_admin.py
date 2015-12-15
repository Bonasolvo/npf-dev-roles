from npf.core.modelaudit.admin import AuditFieldsAdminMixin
from npf.core.xmin.admin import XminAdmin
from django import forms
from django.contrib import admin
from npf.contrib.common.validators import MinLengthValidator, MaxLengthValidator
from npf.contrib.address.forms import AddressField
from django.db.models import ObjectDoesNotExist
from npf.core.xmin.admin import XminGenericTabularInline, getter_for_related_field
from npf.contrib.subject.models import PensionFund
from npf.contrib.subject import models as subject

class PensionFundForm(forms.ModelForm):

    class Meta:
        model = PensionFund
        fields = '__all__'

    required_fields = [
        'name', 'license', 'license_issue_date', 'legal_form', 'ovd', 'inn', 'okpo', 'registration', 'region',
        'legal_address__index', 'legal_address__street', 'legal_address__house', 'actual_address__index',
        'actual_address__street', 'actual_address__house', 'postal_address__index', 'postal_address__street',
        'postal_address__house']

    name = forms.CharField(label='Название')

    legal_address__index = forms.IntegerField(label='Почтовый индекс',
                                              validators=[MinLengthValidator(6), MaxLengthValidator(6)])

    legal_address__street = AddressField(label='Улица')
    legal_address__house = forms.IntegerField(label='Дом')
    legal_address__corps = forms.CharField(label='Корпус', max_length=2, required=False)
    legal_address__apartment = forms.IntegerField(label='Офис', required=False)

    actual_address__index = forms.IntegerField(label='Почтовый индекс',
                                               validators=[MinLengthValidator(6), MaxLengthValidator(6)])

    actual_address__street = AddressField(label='Улица')
    actual_address__house = forms.IntegerField(label='Дом')
    actual_address__corps = forms.CharField(label='Корпус', max_length=2, required=False)
    actual_address__apartment = forms.IntegerField(label='Офис', required=False)

    postal_address__index = forms.IntegerField(label='Почтовый индекс',
                                               validators=[MinLengthValidator(6), MaxLengthValidator(6)])

    postal_address__street = AddressField(label='Улица')
    postal_address__house = forms.IntegerField(label='Дом')
    postal_address__corps = forms.CharField(label='Корпус', max_length=2, required=False)
    postal_address__apartment = forms.IntegerField(label='Офис', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            try:
                self.fields[field].required = field in self.required_fields
            except KeyError:
                pass

        try:
            address = self.instance.legal_address
            self.fields['legal_address__index'].initial = address.index
            self.fields['legal_address__street'].initial = address.street
            self.fields['legal_address__house'].initial = address.house
            self.fields['legal_address__corps'].initial = address.corps
            self.fields['legal_address__apartment'].initial = address.apartment
        except (ObjectDoesNotExist, AttributeError):
            pass

        try:
            address = self.instance.actual_address
            self.fields['actual_address__index'].initial = address.index
            self.fields['actual_address__street'].initial = address.street
            self.fields['actual_address__house'].initial = address.house
            self.fields['actual_address__corps'].initial = address.corps
            self.fields['actual_address__apartment'].initial = address.apartment
        except (ObjectDoesNotExist, AttributeError):
            pass

        try:
            address = self.instance.postal_address
            self.fields['postal_address__index'].initial = address.index
            self.fields['postal_address__street'].initial = address.street
            self.fields['postal_address__house'].initial = address.house
            self.fields['postal_address__corps'].initial = address.corps
            self.fields['postal_address__apartment'].initial = address.apartment
        except (ObjectDoesNotExist, AttributeError):
            pass

    def save(self, commit=True):
        instance = super().save(commit)

        legal_address__index = self.cleaned_data.get('legal_address__index', None)
        legal_address__street = self.cleaned_data.get('legal_address__street', None)
        legal_address__house = self.cleaned_data.get('legal_address__house', None)
        legal_address__corps = self.cleaned_data.get('legal_address__corps', None)
        legal_address__apartment = self.cleaned_data.get('legal_address__apartment', None)

        actual_address__index = self.cleaned_data.get('actual_address__index', None)
        actual_address__street = self.cleaned_data.get('actual_address__street', None)
        actual_address__house = self.cleaned_data.get('actual_address__house', None)
        actual_address__corps = self.cleaned_data.get('actual_address__corps', None)
        actual_address__apartment = self.cleaned_data.get('actual_address__apartment', None)

        postal_address__index = self.cleaned_data.get('postal_address__index', None)
        postal_address__street = self.cleaned_data.get('postal_address__street', None)
        postal_address__house = self.cleaned_data.get('postal_address__house', None)
        postal_address__corps = self.cleaned_data.get('postal_address__corps', None)
        postal_address__apartment = self.cleaned_data.get('postal_address__apartment', None)

        if legal_address__index and legal_address__street and legal_address__house:
            try:
                legal_address = instance.legal_address
                legal_address.index = legal_address__index
                legal_address.street = legal_address__street
                legal_address.house = legal_address__house
                legal_address.corps = legal_address__corps
                legal_address.apartment = legal_address__apartment
                legal_address.save()
            except (ObjectDoesNotExist, AttributeError):
                RelatedModel = instance._meta.get_field('legal_address').rel.to
                fields = {
                    'index': legal_address__index,
                    'street': legal_address__street,
                    'house': legal_address__house,
                    'corps': legal_address__corps,
                    'apartment': legal_address__apartment
                }
                instance.legal_address = RelatedModel.objects.create(**fields)

        if actual_address__index and actual_address__street and actual_address__house:
            try:
                actual_address = instance.actual_address
                actual_address.index = actual_address__index
                actual_address.street = actual_address__street
                actual_address.house = actual_address__house
                actual_address.corps = actual_address__corps
                actual_address.apartment = actual_address__apartment
                actual_address.save()
            except (ObjectDoesNotExist, AttributeError):
                RelatedModel = instance._meta.get_field('actual_address').rel.to
                fields = {
                    'index': actual_address__index,
                    'street': actual_address__street,
                    'house': actual_address__house,
                    'corps': actual_address__corps,
                    'apartment': actual_address__apartment
                }
                instance.actual_address = RelatedModel.objects.create(**fields)

        if postal_address__index and postal_address__street and postal_address__house:
            try:
                postal_address = instance.postal_address
                postal_address.index = postal_address__index
                postal_address.street = postal_address__street
                postal_address.house = postal_address__house
                postal_address.corps = postal_address__corps
                postal_address.apartment = postal_address__apartment
                postal_address.save()
            except (ObjectDoesNotExist, AttributeError):
                RelatedModel = instance._meta.get_field('postal_address').rel.to
                fields = {
                    'index': postal_address__index,
                    'street': postal_address__street,
                    'house': postal_address__house,
                    'corps': postal_address__corps,
                    'apartment': postal_address__apartment
                }
                instance.postal_address = RelatedModel.objects.create(**fields)

        return instance


class PensionFundAdmin(AuditFieldsAdminMixin, XminAdmin):
    form = PensionFundForm

    list_display = [
        'name', 'management_company', 'license', 'license_issue_date', 'legal_form', 'ovd', 'inn', 'registration',
        'region', 'legal_address__index', 'legal_address__street', 'legal_address__house', 'legal_address__corps',
        'legal_address__apartment', 'actual_address__index', 'actual_address__street', 'actual_address__house',
        'actual_address__corps', 'actual_address__apartment', 'postal_address__index', 'postal_address__street',
        'postal_address__house', 'postal_address__corps', 'postal_address__apartment', 'okpo', 'phone']

    list_filter = [
        'name', 'management_company', 'license', 'license_issue_date', 'legal_form', 'ovd', 'inn', 'registration',
        'region', 'legal_address__index', 'legal_address__street', 'legal_address__house', 'legal_address__corps',
        'legal_address__apartment', 'actual_address__index', 'actual_address__street', 'actual_address__house',
        'actual_address__corps', 'actual_address__apartment', 'postal_address__index', 'postal_address__street',
        'postal_address__house', 'postal_address__corps', 'postal_address__apartment', 'okpo', 'phone'
    ]

    search_fields = ['name']

    fieldsets = (
        (None, {'fields': [
            'name', 'management_company', 'license', 'license_issue_date', 'legal_form',
            'okpo', 'ovd', 'inn', 'registration', 'region', 'notes', 'additional_information']}),
        ('Юридический адрес', {'fields': [
            'legal_address__index', 'legal_address__street', 'legal_address__house', 'legal_address__corps',
            'legal_address__apartment']}),
        ('Фактический адрес', {'fields': [
            'actual_address__index', 'actual_address__street', 'actual_address__house', 'actual_address__corps',
            'actual_address__apartment']}),
        ('Почтовый адрес', {'fields': [
            'postal_address__index', 'postal_address__street', 'postal_address__house', 'postal_address__corps',
            'postal_address__apartment']}),
        ('Контакты', {'fields': ['phone', 'fax', 'contacts']})
    )

    # Юридический адрес

    legal_address__index = getter_for_related_field('legal_address__index', short_description='Почтовый индекс')

    legal_address__street = getter_for_related_field('legal_address__street', short_description='Улица')

    legal_address__house = getter_for_related_field('legal_address__house', short_description='Дом')

    legal_address__corps = getter_for_related_field('legal_address__corps', short_description='Корпус')

    legal_address__apartment = getter_for_related_field('legal_address__apartment', short_description='Квартира')

    # Фактический адрес

    actual_address__index = getter_for_related_field('actual_address__index', short_description='Почтовый индекс')

    actual_address__street = getter_for_related_field('actual_address__street', short_description='Улица')

    actual_address__house = getter_for_related_field('actual_address__house', short_description='Дом')

    actual_address__corps = getter_for_related_field('actual_address__corps', short_description='Корпус')

    actual_address__apartment = getter_for_related_field('actual_address__apartment', short_description='Квартира')

    # Почтовый адрес

    postal_address__index = getter_for_related_field('postal_address__index', short_description='Почтовый индекс')

    postal_address__street = getter_for_related_field('postal_address__street', short_description='Улица')

    postal_address__house = getter_for_related_field('postal_address__house', short_description='Дом')

    postal_address__corps = getter_for_related_field('postal_address__corps', short_description='Корпус')

    postal_address__apartment = getter_for_related_field('postal_address__apartment', short_description='Квартира')

    columns = [{
        'dataIndex': 'name',
        'text': 'Название',
        'width': 200,
    }, {
        'dataIndex': 'management_company',
        'width': 200
    }, {
        'dataIndex': 'license'
    }, {
        'dataIndex': 'license_issue_date',
        'width': 150
    }, {
        'dataIndex': 'legal_form',
        'width': 200
    }, {
        'dataIndex': 'ovd'
    }, {
        'dataIndex': 'inn'
    }, {
        'dataIndex': 'registration',
        'width': 150
    }, {
        'dataIndex': 'region',
        'width': 150
    }, {
        'dataIndex': 'okpo'
    }, {
        'dataIndex': 'phone'
    }, {
        'text': 'Юридический адрес',
        'columns': [{
            'dataIndex': 'legal_address__index',
            'width': 110,
            'filter': 'string'
        }, {
            'dataIndex': 'legal_address__street',
            'width': 350,
            'filter': 'address'
        }, {
            'dataIndex': 'legal_address__house',
            'filter': 'string'
        }, {
            'dataIndex': 'legal_address__corps',
            'filter': 'string'
        }, {
            'dataIndex': 'legal_address__apartment',
            'filter': 'string'
        }]
    }, {
        'text': 'Фактический адрес',
        'columns': [{
            'dataIndex': 'actual_address__index',
            'width': 110,
            'filter': 'string'
        }, {
            'dataIndex': 'actual_address__street',
            'width': 350,
            'filter': 'address'
        }, {
            'dataIndex': 'actual_address__house',
            'filter': 'string'
        }, {
            'dataIndex': 'actual_address__corps',
            'filter': 'string'
        }, {
            'dataIndex': 'actual_address__apartment',
            'filter': 'string'
        }]
    }, {
        'text': 'Почтовый адрес',
        'columns': [{
            'dataIndex': 'postal_address__index',
            'width': 110,
            'filter': 'string'
        }, {
            'dataIndex': 'postal_address__street',
            'width': 350,
            'filter': 'address'
        }, {
            'dataIndex': 'postal_address__house',
            'filter': 'string'
        }, {
            'dataIndex': 'postal_address__corps',
            'filter': 'string'
        }, {
            'dataIndex': 'postal_address__apartment',
            'filter': 'string'
        }]
    }]

admin.site.register(subject.PensionFund, PensionFundAdmin)
