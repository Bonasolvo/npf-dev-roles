Ext.define('Dashboard.controller.Dashboard', {
    // Загрузка и обработка закладок

    extend: 'Ext.app.Controller',

    requires  : [
        'Dashboard.controller.ServerEvents'
    ],

    views: [
        'dashboard.Layout',
        'dashboard.Header',
        'dashboard.Options',
        'dashboard.MainMenu',
        'dashboard.Bookmarks',
        'dashboard.RecentActions',
        'dashboard.Tabs',
        'dashboard.MyTasks',
        'dashboard.AppointmentWorkflowButton',
        'dashboard.FakeWorkflowButton',
        'dashboard.BreadcrumbsContainer',
        'dashboard.Breadcrumbs',
        //'dashboard.CloseIPSWorkflowButton'
    ],

    stores: [
        'MainMenu',
        'Bookmarks'
    ],

    models: [
        'MenuItem',
        'Bookmark'
    ],

    init: function () {
        this.loadMainMenu();
        this.loadBookmarks();

        this.control({
            // Обработчики событий для закладок
            Bookmarks: {
                itemclick: this.onBookmarkOpen,
                itemcontextmenu: this.onBookmarkItemContextMenu
            },

            'menuitem[name=dashboard-bookmark-context-menu-item-add-new]': {
                click: this.onBookmarkContextMenuAddNewItemClick
            },

            'menuitem[name=dashboard-bookmark-context-menu-item-list-all]': {
                click: this.onBookmarkContextMenuListAllItemClick
            },

            'menuitem[name=dashboard-bookmark-context-menu-item-delete]': {
                click: this.onBookmarkContextMenuDeleteItemClick
            }
        });
    },

    loadBookmarks: function () {
        this.getStore('Bookmarks').load();
    },

    loadMainMenu: function () {
        var store = this.getStore('MainMenu'),
            settings = Xmin.settings,
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
    },

    onBookmarkItemContextMenu: function(view, record, item, index, e, eOpts) {
        e.stopEvent();

        view.all.elements.forEach(function(element, index, array){
            if (element.contextMenu)
                element.contextMenu.hide();
        });

        if (item.contextMenu == undefined) {
            // Создаем контекстное меню для закладки
            var add_url = record.get('add_url'),
                admin_url = record.get('admin_url'),
                delete_url = record.get('id'),
                menu_items = [
                    {
                        text: Xmin.util.Text.capfirst(record.get('__str__')),
                        canActivate: false,
                        iconCls: 'xmin-modellist-context-menu-item-default-icon',
                        cls: 'xmin-modellist-context-menu-title'
                    },
                    '-'
                ];

            if (add_url)
                menu_items.push(
                    {
                        text: 'Добавить запись',
                        cls: 'xmin-modellist-context-menu-item-routable',
                        iconCls: 'xmin-modellist-context-menu-item-add-new-icon',
                        name: 'dashboard-bookmark-context-menu-item-add-new',
                        token: add_url
                    }
                );

            if (admin_url)
                menu_items.push(
                    {
                        text: 'Просмотреть все',
                        cls: 'xmin-modellist-context-menu-item-routable',
                        iconCls: 'xmin-modellist-context-menu-item-list-all-icon',
                        name: 'dashboard-bookmark-context-menu-item-list-all',
                        token: admin_url
                    }
                );

            menu_items.push(
                {
                    text: 'Удалить закладку',
                    cls: 'xmin-modellist-context-menu-item-routable',
                    iconCls: 'xmin-modellist-context-menu-item-list-all-icon',
                    name: 'dashboard-bookmark-context-menu-item-delete',
                    token: delete_url
                }
            );

            item.contextMenu = Ext.create('Ext.menu.Menu', {
                items: menu_items
            });
        }

        item.contextMenu.showAt(e.getXY());
    },

    onBookmarkOpen : function(view, record, item, index, e, eOpts){
        var router = this.getController('Router'),
            add_url = record.get('add_url'),
            admin_url = record.get('admin_url');

        if (!admin_url)
            router.navigate(record.get('add_url'));
        else
            router.navigate(record.get('admin_url'));
    },

    onBookmarkContextMenuAddNewItemClick: function (menuitem, e, eOpts) {
        var router = this.getController('Router');
        router.navigate(menuitem.token);
    },

    onBookmarkContextMenuListAllItemClick: function (menuitem, e, eOpts) {
        var router = this.getController('Router');
        router.navigate(menuitem.token);
    },

    onBookmarkContextMenuDeleteItemClick: function (menuitem, e, eOpts) {
        var store = this.getStore('Bookmarks');

        Ext.Ajax.request({
            method: 'DELETE',
            url: '/bookmark/',
            headers: { 'Content-Type': 'application/json; charset=UTF-8' },
            params: Ext.JSON.encode([menuitem.token]),
            success: function(response) {
                var app_response = Ext.JSON.decode(response.responseText);
                if (app_response.success) {
                    store.load();
                }
            }
        });
    }

});
