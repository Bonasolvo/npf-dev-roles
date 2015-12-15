from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from npf.core.xmin.admin import XminAdmin
from npf.core.printform.models import *


class TemplateAdmin(XminAdmin):
    list_display = ['pk', 'name', 'file', 'model']
    list_display_links = ['pk']

class CTypeAdmin(XminAdmin):
    list_display = ['app_label', 'model']
    list_display_links = []

    columns = [{
        'dataIndex': 'app_label',
        'flex': 1
    }, {
        'dataIndex': 'model',
        'flex': 1
    }]

    def suggest_items(self, model):
        ids = []
        for model, model_admin in admin.site._registry.items():
            if ContentType.objects.get_for_model(model).id != ContentType.objects.get_for_model(ContentType).id:
                ids.append(ContentType.objects.get_for_model(model).id)
        return ContentType.objects.filter(pk__in=ids)


admin.site.register(Template, TemplateAdmin)
admin.site.register(ContentType, CTypeAdmin)
