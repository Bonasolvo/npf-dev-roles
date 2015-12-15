Ext.tip.QuickTipManager.init();

Ext.Loader.setConfig({
    enabled: true,
    paths: {
        'Xmin': '/static/xmin',
        'Ext.ux': '//cdn.sencha.com/ext/gpl/5.1.0/examples/ux'
    }
});

Ext.Ajax.on({
    // Для всех ajax запросов перед отправкой добавляем СSRF токен, если метод небезопасен
    beforerequest: function (conn, options, eOpts) {
        function csrfSafeMethod(method) {
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        }

        if (!csrfSafeMethod(options.method)) {
            Ext.apply(options, {
                headers: {
                    'X-CSRFToken': Ext.util.Cookies.get('csrftoken')
                }
            });
        }
    }
});

Ext.application({
    name: 'Dashboard',
    appFolder: '/static/dashboard',

    controllers: [
        'Dashboard',
        'Router',
        'ServerEvents',
        'Admin'
    ],

    launch: function() {
        Xmin.application = this;

        Ext.create('Ext.container.Viewport', {
            layout: 'fit',
            items: {
                xtype: 'Dashboard'
            }
        });
    }
});