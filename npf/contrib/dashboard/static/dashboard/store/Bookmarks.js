Ext.define('Dashboard.store.Bookmarks', {
    extend: 'Ext.data.Store',
    model: 'Dashboard.model.Bookmark',

    proxy: {
        type: 'ajax',
        url: '/bookmark/',
        reader: {
            type: 'json',
            successProperty: 'success',
            rootProperty: 'bookmarks'
        },
        writer: {
            type: 'json'
        }
    }
});