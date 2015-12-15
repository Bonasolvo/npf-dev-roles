from npf.core.xmin.admin import XminAdmin


class DocumentTypeAdmin(XminAdmin):
    list_display = ['type_name']
    columns = [{
        'dataIndex': 'type_name',
        'flex': 1
    }]
