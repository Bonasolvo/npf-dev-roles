"""
NPF roles admin module
"""
from django.contrib import admin

from npf.core.xmin.admin import XminAdmin
from npf.contrib.role.models import Role

admin.site.register(Role, XminAdmin)
