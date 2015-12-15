Ext.define('Dashboard.view.dashboard.Options', {
    extend: 'Ext.Container',
    alternateClassName: 'Dashboard.Options',
    xtype: 'dashboardOptions',

    id: 'app-header-options',
    margin: '0 10 0 0',
    layout: 'hbox',

    initComponent: function () {

        var menu = Ext.create('Ext.menu.Menu', {
            items: [{
                text: 'Изменить пароль',
                handler: function () {
                    var router = Dashboard.app.getController('Router');
                    router.navigate(Xmin.settings.urls.password_change);
                }
            }, '-', {
                text: 'Выйти',
                handler: function () {
                    var router = Dashboard.app.getController('Router');
                    router.navigate(Xmin.settings.urls.logout);
                }
            }]
        });

        this.items = [{
            xtype: 'component',
            id: 'app-header-options-btn',
            margin: '0 5 0 0',
            listeners: {
                scope: this,
                click: function (e) {
                    menu.showBy(this);
                },
                element: 'el'
            }
        }];

        this.callParent();
    }
});