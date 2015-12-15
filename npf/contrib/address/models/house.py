from django.db import models
from django.utils.translation import ugettext_lazy as _
from fias.fields import AddressField
from .street_lazy import StreetLazy


class House(StreetLazy):
    index = models.PositiveIntegerField(verbose_name='Почтовый индекс', blank=True, null=True)

    house = models.PositiveSmallIntegerField(_('Дом'), null=True, blank=True)
    fias_house = AddressField(verbose_name=_('Дом'), related_name='+', null=True, blank=True, db_column='fiashouse')
    corps = models.CharField(_('Корпус'), max_length=2, null=True, blank=True)
    apartment = models.PositiveSmallIntegerField(_('Квартира'), null=True, blank=True)

    class Meta:
        db_table = 'zlk_house'