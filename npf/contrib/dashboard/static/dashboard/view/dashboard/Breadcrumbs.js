Ext.define('Dashboard.view.dashboard.Breadcrumbs', {
    extend: 'Ext.toolbar.Breadcrumb',
    alias: 'widget.Breadcrumb',
    xtype: 'dashboardBreadcrumbs',

    initComponent: function () {

        function createStore(model) {
            var store = Ext.create('Dashboard.store.MainMenu', {
                model: Ext.getCmp("main_menu_tree").getStore().model
            });
        var settings = Xmin.settings,
            data = {
                text: 'Root',
                expanded: true,
                children: []
            };

        for (var app_key in settings.app_list) {
            if (!settings.app_list.hasOwnProperty(app_key))
                continue;

            var app = settings.app_list[app_key],
                node = {
                    text: app.name,
                    expanded: true,
                    children: []
                };

            for (var model_key in app.models) {
                if (!app.models.hasOwnProperty(model_key))
                    continue;

                var model = app.models[model_key];

                node.children.push({
                    app: app.app,
                    model: model.model,
                    text: model.verbose_name_plural,
                    text_child: model.verbose_name,
                    add_url: model.add_url,
                    admin_url: model.admin_url,
                    perms: model.perms,
                    leaf: true
                });
            }
            data.children.push(node);
        }

        store.suspendEvents(true);
        store.setRootNode(data);
        store.resumeEvents();

        var mainMenu = Ext.getCmp("main_menu_tree");
        store.each(function(r) {

            var result = mainMenu.getStore().findBy(function(record, id){
                if(record.raw.text.toLocaleLowerCase() == r.raw.text.toLocaleLowerCase())
                    return id;
            });

            if(result != -1) {
                var mainMenuRecord = mainMenu.getStore().getAt(result);
                r.set("id", mainMenuRecord.id);
                r.commit(true);
            }
        });

        return store;
    }
        this.store = createStore();
        this.callParent();
    },

    listeners: {
        selectionchange: function (panel, node, eOpts) {
            var mainMenu = Ext.getCmp("main_menu_tree");
            var record = mainMenu.getStore().getById(node.parent1Id || node.id);

            if(record != null) {
                var child = this.getStore().getRoot().findChild('id', 'child', 5);
                if(child)
                    child.remove();
                mainMenu.changeActiveItem(record);
            }
        },
    }
});