Ext.define('Dashboard.model.MenuItem', {
    extend: 'Ext.data.Model',
    fields: [
        { name: 'app', type: 'string' },
        { name: 'model', type: 'string' },
        { name: 'text', type: 'string' },
        { name: 'add_url', type: 'string' },
        { name: 'admin_url', type: 'string' },
        { name: 'perms', type: 'auto' }
    ]
});