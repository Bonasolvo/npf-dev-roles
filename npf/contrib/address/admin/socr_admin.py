from npf.core.xmin.admin import XminAdmin


class SocrAdmin(XminAdmin):
    """
    Список адресных сокращений (обл., г., р-н.)
    """
    list_display = ['level', 'item_weight', 'scname', 'socrname']
    list_filter = ['scname', 'item_weight', 'socrname']
    fields = ['scname', 'socrname', 'level', 'item_weight']
    readonly_fields = ['level', 'scname', 'socrname']
    ordering = ['level', 'item_weight', 'scname']
    columns = [{
        'dataIndex': 'level',
        'flex': 1
    }, {
        'dataIndex': 'item_weight',
        'flex': 1
    }, {
        'dataIndex': 'scname',
        'flex': 1
    }, {
        'dataIndex': 'socrname',
        'flex': 1
    }]

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False