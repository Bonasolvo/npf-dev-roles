from npf.core.xmin.admin import XminAdmin


class ScriptCommandAdmin(XminAdmin):
    list_display = ['name', 'description', 'command']
    columns = [{
        'dataIndex': 'name',
        'flex': 1
    }, {
        'dataIndex': 'description',
        'flex': 1
    }, {
        'dataIndex': 'command',
        'flex': 1
    }]
