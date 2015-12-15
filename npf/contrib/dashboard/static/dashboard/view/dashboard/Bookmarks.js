Ext.define('Dashboard.view.dashboard.Bookmarks', {
    extend : 'Ext.view.View',
    alias  : 'widget.Bookmarks',

    requires  : [
        'Xmin.util.Text',
        'Xmin.util.GetLines'
    ],

    id: 'app-dashboard-bookmarks',

    store: 'Bookmarks',

    deferInitialRefresh: false,

    tpl: Ext.create('Ext.XTemplate',
        '<ul class="xmin-modellist-buttons">',
        '<tpl for=".">',
            '<li>',
                '<a class="{model}">{[Xmin.util.Text.capfirst(values.__str__)]}</a>',
            '</li>',
        '</tpl>',
        '</ul>'
    ),

    cls: 'xmin-modellist',
    itemSelector: 'a',
    autoScroll  : true,

    listeners: {
        beforecontainermouseover: function() {
            this.dropzone.isTarget = true;
        },
        render: function(panel) {
            var self = this;
            // Создаем drag-and-drop область
            panel.dropTarget = Ext.create('Ext.dd.DropTarget', panel.el, {
                ddGroup: 'MainMenu2LaunchPad',

                // Вешаем обработчики событий
                notifyEnter: function(source, e, data) {
                    var classname = data.item.getAttribute("class");
                    if (classname.indexOf("DELETION") > -1) {
                        panel.dropTarget.isTarget = false;
                    }
                },
                notifyDrop: function(source, e, data) {
                    function addItemsRecursive(item) {
                        if (item.leaf) {
                            bookmarks.push({
                                __str__: item.text,
                                record_id: item.record_id,
                                add_url: item.add_url,
                                admin_url: item.admin_url,
                                content_type: {
                                    app_label: item.app,
                                    model: item.model
                                }
                            });
                            return;
                        }

                        var childs = item.children;

                        for (var key in childs) {
                            if (!childs.hasOwnProperty(key))
                                continue;

                            var child = childs[key];
                            addItemsRecursive(child);
                        }
                    }

                    var bookmarks = [];

                    var records = source.dragData.records;

                    // Добавляем в рабочую область все приложения рекурсивно
                    // Пр.: Если перетаскиваем группу, то на рабочую область добавятся все
                    // приложения из группы
                    for (var key in records) {
                        if (!records.hasOwnProperty(key))
                            continue;

                        addItemsRecursive(records[key].data);
                    }

                    Ext.Ajax.request({
                        method: 'POST',
                        url: '/bookmark/',
                        headers: { 'Content-Type': 'application/json; charset=UTF-8' },
                        params: Ext.JSON.encode(bookmarks),
                        success: function(response) {
                            var app_response = Ext.JSON.decode(response.responseText);
                            if (app_response.success) {
                                var resp = app_response.bookmarks;
                                for (i = 0; i < resp.length; i++) {
                                    if ('bookmark_name' in resp[i]) {
                                        resp[i]['__str__'] = resp[i]['bookmark_name'];
                                    }
                                }
                                self.store.loadData(resp, true);
                            }
                        }
                    });
                }
            });
            this.dropzone = panel.dropTarget;
        },
        refresh: function () {
            $('.xmin-modellist-buttons li a').each(function(){
                var text = $(this).text();
                var lines_result = Xmin.util.GetLines.func($(this));
                var lines = lines_result[0];
                var bottom = lines_result[1];
                if (lines > 2) {
                    $(this).text(bottom);
                    $(this).attr('title', text);
                }
            });
        }
    }
});