from .defaults import *
from django.contrib.admin import site
from django.contrib.admin.actions import delete_selected
from django.conf.locale.ru import formats as ru_formats

site.site_title = 'NPF CRM Developement'
site.site_header = 'NPF CRM Developement'
delete_selected.short_description = 'Удалить выбранные записи'

ru_formats.DATETIME_FORMAT = "d.m.Y H:i:s"
ru_formats.DATE_FORMAT = 'd.m.Y'
ru_formats.TIME_FORMAT = 'H:i:s'

try:
    from .development import *
except ImportError:
    pass
