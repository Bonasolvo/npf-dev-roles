from npf.core.xmin.admin import XminAdmin


class LegalFormAdmin(XminAdmin):
    list_display = ['short_name', 'name']
    list_filter = ['short_name', 'name']
    search_fields = ['short_name', 'name']
    ordering = ['short_name']
    columns = [{
        'dataIndex': 'short_name',
        'flex': 1
    }, {
        'dataIndex': 'name',
        'flex': 1
    }]