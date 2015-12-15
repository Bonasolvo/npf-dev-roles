Ext.define('Dashboard.view.dashboard.Header', {
    extend: 'Ext.Container',
    alternateClassName: 'Dashboard.Header',
    xtype: 'dashboardHeader',

    id: 'app-header',
    title: Xmin.settings.site_title,
    height: 52,

    layout: {
        type: 'hbox',
        align: 'middle'
    },

    initComponent: function() {
        document.title = this.title;

        this.items = [{
            xtype: 'component',
            id: 'app-header-logo'
        },{
            xtype: 'component',
            id: 'app-header-title',
            html: this.title,
            flex: 1
        },{
            xtype: 'tbtext',
            text: Ext.String.format('Добро пожаловать, <b>{0}</b>.', Xmin.settings.user.name),
            style: 'padding-top: 2px'
        },{
            xtype: 'component',
            width: 10
        },
        {
            xtype: 'dashboardOptions',
            id: 'app-header-options'
        }];

        this.callParent();
    }
});