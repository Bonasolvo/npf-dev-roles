from django.contrib import admin

from npf.core.xmin.admin import XminAdmin
from .models import Bookmark


class BookmarkAdmin(XminAdmin):
    list_display = ('content_type', 'record_id', 'user')

admin.site.register(Bookmark, BookmarkAdmin)