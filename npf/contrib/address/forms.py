from django.forms import CharField
from fias.widgets import AddressSelect2
from fias.config import FIAS_SUGGEST_VIEW
from .validators import AddressValidator


class AddressField(CharField):
    widget = AddressSelect2(data_view=FIAS_SUGGEST_VIEW)
    default_validators = [AddressValidator()]
