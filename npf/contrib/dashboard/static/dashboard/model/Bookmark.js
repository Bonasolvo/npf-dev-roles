Ext.define('Dashboard.model.Bookmark', {
    extend: 'Ext.data.Model',
    fields: [
        { name: '__str__', type: 'string' },
        { name: 'id', type: 'int' },
        { name: 'record_id', type: 'int' },
        { name: 'content_type', type: 'auto' },
        { name: 'add_url', type: 'string' },
        { name: 'admin_url', type: 'string' },
    ]
});