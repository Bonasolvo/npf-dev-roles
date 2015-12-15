Ext.define('Dashboard.view.dashboard.BreadcrumbsContainer', {
    extend: 'Ext.Container',
    alternateClassName: 'Dashboard.Breadcrumbs',
    xtype: 'dashboardBreadcrumbsContainer',

    id: 'app-breadcrumbs',
    height: 52,

    layout: {
        type: 'hbox',
        align: 'middle'
    },

    initComponent: function () {
        this.items = [{
            xtype: 'dashboardBreadcrumbs',
            id: 'breadcrumbs',
            store: 'MainMenu'
        }];
        this.callParent();
    }
});