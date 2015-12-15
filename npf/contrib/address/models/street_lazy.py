from django.db import models
from django.utils.translation import ugettext_lazy as _
from fias.fields import AddressField
from .address import Address


class StreetLazy(models.Model):

    class Meta:
        abstract = True

    street = models.CharField(_('Улица'), max_length=255, blank=True, editable=False, db_index=True)
    fias_street = AddressField(verbose_name=_('Улица'), related_name='+', null=True, blank=True)

    def __str__(self):
        return self.street

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        prefix, address = Address.objects.by_term(self.street, exact=True)

        if len(address) == 1:
            self.fias_street_id = address[0].pk
        else:
            self.fias_street_id = None

        super().save(force_insert, force_update, using, update_fields)