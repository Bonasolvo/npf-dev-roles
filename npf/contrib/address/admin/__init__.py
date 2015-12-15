from django.contrib import admin
from fias.models import SocrBase
from npf.contrib.address.models import Socr
from .socr_admin import SocrAdmin


admin.site.unregister(SocrBase)
admin.site.register(Socr, SocrAdmin)