Ext.define('Dashboard.controller.Admin', {
    extend: 'Xmin.controller.Admin',
    requires  : [
        'Xmin.util.CompileId'
    ],

    init: function() {
        // Формирование меню инструментов:
        //  1. Поиск
        //  2. Печать
        //  3. Экспорт в excel

        var me = this;

        me.callParent();

        me.control({
            // Добавление обработчиков событий для элементов управления
            'textfield[name="search"]': {
             specialkey: function(field, e, eOpts) {
                if (e.getKey() == e.ENTER) {
                    me.onChangeListSearch(field, e, eOpts);
                }
            }
            },
            'tool[type="search"]': {
                click: me.onChangeListSearch
            },
            'tool[type="plus"]': {
                click: me.onAddClick
            },
            'tool[type="gear"]': {
                click: me.export_excel
            }
        });

        me.registerWorkflowUrls();
    },

    onChangeListSearch : function(button, event, eOpts) {
        function _grid_search () {
            var tree = false;
            var this_window = button.up('panel'),
                query_field = this_window.down('textfield[name="search"]'),
                grid = this_window.activeTab.down('grid'),
                inlineTabPanel = button.up('panel').activeTab.down('panel'),
                inlineActiveTab = inlineTabPanel.activeTab;

            // Проверка текущей активной вкладки
            // и загрузка записей по передаваемой строке поиска

            if (!grid) {
                var grid = this_window.activeTab.down('tree-grid');
                tree = true;
            }

            if (inlineActiveTab) {
                var inlineActiveTabIndex = inlineTabPanel.items.findIndex('id', inlineActiveTab.id);
                if (inlineActiveTabIndex > 0) {
                    grid = inlineActiveTab.down('panel');
                }
            }

            var store = grid.getStore(),
                proxy = store.getProxy();

            proxy.extraParams['q'] = query_field.getValue();
            if (tree) {
                store.loadData([], false);
            }
            store.reload();
        }

        var tab_title = Ext.getCmp('TabPanel').getActiveTab().title;
        if (tab_title != 'Закладки') {
            _grid_search();
        }
    },

    onAddClick: function(button, event, eOpts) {
        var config = button.up('panel').activeTab.config.items[0],
            inlineTabPanel = button.up('panel').activeTab.down('panel'),
            inlineActiveTab = inlineTabPanel.activeTab;

        if (inlineActiveTab) {
            var inlineActiveTabIndex = inlineTabPanel.items.findIndex('id', inlineActiveTab.id);

            // Add row to inline change list
            if (inlineActiveTabIndex > 0) {
                var changeListInlinePanel = inlineActiveTab.down('panel');
                changeListInlinePanel.addNewRow();
                return;
            }
        }

        // navigate to add page
        var model_token = config.xmin_model.admin_url,
            add_item_token = model_token + 'add/',
            router = this.getController('Router');

        router.navigate(add_item_token);
    },

    changeListWindowFactory: function(config) {
        var window_config = {
            title: Xmin.util.Text.capfirst(config.verbose_name_plural)
        };
        if ('is_tree' in config) {
            return this.routableTabFactory(config, 'Xmin.view.admin.ChangeListPanelTree', window_config);
        }
        return this.routableTabFactory(config, 'Xmin.view.admin.ChangeListPanel', window_config);
    },

    itemAddWindowFactory: function(config) {
        var window_config = {
            title : Xmin.util.Text.capfirst(config.verbose_name)
        };
        return this.routableTabFactory(config, 'Xmin.view.admin.ItemChangePanel', window_config);
    },

    itemChangeWindowFactory: function(config) {
        var window_config = {
            title : Xmin.util.Text.capfirst(config.verbose_name)
        };
        return this.routableTabFactory(config, 'Xmin.view.admin.ItemChangePanel', window_config);
    },

    changePassword: function () {
        Ext.onReady(function() {
            tabs = Ext.getCmp('TabPanel');
            tabs.activeTab.setLoading(gettext('Loading...'));

            var tab = tabs.add({
                title: 'Изменение пароля',
                closable: true,
                layout: 'fit',
                items: [
                    Ext.create('Xmin.view.admin.ChangePasswordPanel')
                ]
            });

            tabs.activeTab.setLoading(false);
            tabs.setActiveTab(tab);
        });
    },

    changePasswordDone: function () {
        Ext.onReady(function() {
            tabs = Ext.getCmp('TabPanel');
            tabs.activeTab.setLoading(gettext('Loading...'));

            var tab = tabs.add({
                title: 'Пароль изменён',
                closable: true,
                layout: 'fit',
                items: [
                    Ext.create('Xmin.view.admin.ChangePasswordPanelDone')
                ]
            });

            tabs.activeTab.setLoading(false);
            tabs.setActiveTab(tab);
        });
    },

    routableTabFactory: function(model_config, class_path, window_config) {
        Ext.require(class_path);
        return function activateRoutableTab(token) {
            // Загрузка/Активация/Переключение между вкладками.
            // Если вкладка уже открыта, то просто активируем её.
            // Если вкладка ещё не открыта, тогда делаем запрос данных,
            // загружаем новую вкладку и после этого активируем.
            var panel = Ext.ComponentQuery.query('panel[xmin_token="'+token+'"]')[0];
            if (panel) {
                var tabs = panel.ownerCt.ownerCt;
                tabs.setActiveTab(panel.ownerCt);
            } else {
                Ext.onReady(function() {
                    // GET CONFIG
                    tabs = Ext.getCmp('TabPanel');
                    tabs.activeTab.setLoading(gettext('Loading...'));

                    Ext.Ajax.request({
                        url: Xmin.settings.urls.xmin_data + token,
                        method: 'GET',
                        success: function(response) {
                            var app_response = Ext.JSON.decode(response.responseText);

                            // RENDER TAB
                            var window_title = window_config ? window_config.title : gettext('Window');

                            if (app_response && app_response.adminform && app_response.adminform.__str__)
                                window_title += ' - ' + Xmin.util.Text.capfirst(app_response.adminform.__str__);

                            var tab = tabs.add({
                                title: window_title,
                                closable: true,
                                border: false,
                                layout: 'fit',
                                items: [
                                    Ext.create(class_path, {
                                        xmin_token: token,
                                        xmin_model: model_config,
                                        xmin_admin: app_response,
                                        border: false
                                    })
                                ]
                            });

                            tabs.activeTab.setLoading(false);
                            tabs.setActiveTab(tab);

                            //$.getScript("/static/workflow/js/make_start_process_buttons.js", function () {
                            //    make_start_process_buttons();
                            //});
                        },
                        failure: function (error) {
                            tabs.activeTab.setLoading(false);
                        }
                    });

                });
            }
        };
    },

    registerWorkflowUrls: function() {
        var router = this.getController('Router'),
            urls = [];

        urls.push({
            pattern: "/workflow/start/*",
            callback: this.workflow
        });

        urls.push({
            pattern: "/workflow/main/*",
            callback: this.workflow
        });

        urls.push({
            pattern: '/workflow/\\d+/*',
            callback: this.workflow
        });

        router.registerUrls(urls);
    },

    workflow: function (url) {
        var new_url = url.replace('/admin','');

        if (url.indexOf('appointment/workflow/start') > -1) {
            var panel = Ext.ComponentQuery.query('panel[xmin_token*="appointment/workflow/start"]')[0];
        }
        else if (url.indexOf('fake/workflow/start') > -1) {
            var panel = Ext.ComponentQuery.query('panel[xmin_token*="fake/workflow/start"]')[0];
        }
        else if (url.indexOf('close_ips/workflow/start') > -1) {
            var panel = Ext.ComponentQuery.query('panel[xmin_token*="close_ips/workflow/start"]')[0];
        }
        else {
            var panel = Ext.ComponentQuery.query('panel[xmin_token="'+url+'"]')[0];
        }

        if (panel) {
            var tabs = panel.ownerCt.ownerCt;
            tabs.setActiveTab(panel.ownerCt);
        } else {
            Ext.onReady(function () {
                Ext.Ajax.request({
                    url: new_url,
                    method: "get",
                    success: function (response) {
                        var resp = response.responseText;
                        tabs = Ext.getCmp('TabPanel');
                        tabs.activeTab.setLoading(gettext('Loading...'));
                        var id = Xmin.util.CompileId.replace_slashes(url);

                        var re = /\/(\d+)\//g;
                        var task_id = url.match(re);

                        Ext.Ajax.request({
                            url: 'workflow/get_xmin_title',
                            method: "get",
                            params: {'url': url, 'task_id': task_id},
                            success: function (response) {
                                var title = Ext.JSON.decode(response.responseText).result;
                                var tab = tabs.add({
                                    title: title,
                                    id: id,
                                    closable: true,
                                    layout: 'fit',
                                    items: [
                                        Ext.create('Ext.Panel', {
                                            xmin_token: url,
                                            html: resp,
                                            autoScroll: true,
                                            listeners: {
                                                afterrender: function () {
                                                    $.getScript("/static/workflow/js/change_href.js", function () {
                                                        change_href();
                                                    });
                                                    $.getScript("/static/workflow/js/strip_href.js", function () {
                                                        strip_href();
                                                    });
                                                    $.getScript("/static/workflow/js/create_form.js", function () {
                                                        create_form();
                                                    });
                                                    $.getScript("/static/workflow/js/create_approve_data.js", function () {
                                                        create_approve_data();
                                                    });
                                                    $.getScript("/static/workflow/js/create_task_info.js", function () {
                                                        create_task_info();
                                                    });
                                                    $.getScript("/static/workflow/js/preselect_document.js", function () {
                                                        preselect_document();
                                                    });

                                                    $.getScript("/static/workflow/js/processes/close_ips/input_acc_number_close_ips.js", function () {
                                                        input_acc_number_close_ips();
                                                    });
                                                    $.getScript("/static/workflow/js/processes/close_ips/close_acc_close_ips.js", function () {
                                                        close_acc_close_ips();
                                                    });
                                                }
                                            }
                                        })
                                    ]
                                });

                        tabs.activeTab.setLoading(false);
                        tabs.setActiveTab(tab);
                        }
                    });
                    }
                });
            });
        }
    },

    export_excel: function(button, event, eOpts) {

        var me = this;

        function _get_panel () {
            var tab = eOpts;
            var title = tab.title;
            var tabs = tab.items.items;
            for (i = 0; i < tabs.length; i++) {
                if (tabs[i].title == title && tabs[i].items) {
                    return Ext.getCmp(tabs[i].items.items[0].id);
                }
            }
        }

        function _get_params () {
            var sort = '';
            var opts = panel.store.lastOptions;
            if (opts.hasOwnProperty('sorters') && opts['sorters'].length) {
                sort = {
                    'direction': opts['sorters'][0]['_direction'],
                    'property': opts['sorters'][0]['_property']
                };
                sort = [sort];
            }
            return sort;
        }

        function _get_filters () {
            var _filters = [];
            var filters = panel.store.filters.items;
            if (!filters.length) return '';
            for (i in filters) {
                _filters.push({
                    'operator': filters[i]['_operator'],
                    'property': filters[i]['_property'],
                    'value': filters[i]['_value']
                })
            }
            return _filters;
        }

        function _get_columns () {
            var _columns = [];
            var columns = panel.columnManager.columns;
            var heading = panel.columnManager.headerCt.config.items;

            for (i in columns) {
                if (columns[i]['dataIndex']) (
                    _columns.push({
                        'name': columns[i]['dataIndex'],
                        'visible': !(columns[i]['hidden'] || columns[i]['hiddenAncestor'])
                    })
                )
            }
            return {'columns': _columns, 'excel_heading': heading};
        }

        function _check_inline_panel(panel) {
            if (panel.activeTab) {
                panel = panel.activeTab.items.items[0]
            }
            return panel;
        }

        var panel = _get_panel();
        if (!panel) return;
        panel = _check_inline_panel(panel);
        if (!panel.columnManager) return;
        var params = _get_columns();
        params['filters'] = _get_filters();
        params['sort'] = _get_params();
        var dc = Math.random().toString().replace('.', '');
        var url = Xmin.settings.urls.xmin_data + panel.xmin_token + '?' + 'export=true&_dc=' + dc;

        me.downloadFile(url, params)
    },

    downloadFile: function (url, params) {

        var body = Ext.getBody(),
            frame = body.createChild({
                tag: 'iframe',
                cls: 'x-hidden',
                name: 'iframe'
            }),
            form = body.createChild({
                tag: 'form',
                method: 'POST',
                cls: 'x-hidden',
                action: url,
                target: 'iframe'
            }),
            csrf = Ext.util.Cookies.get('csrftoken');

        form.createChild({
            tag: 'input',
            type: 'hidden',
            cls: 'x-hidden',
            name: 'csrfmiddlewaretoken',
            value: csrf
        });
        json_string = JSON.stringify(params)
        escaped_json = json_string.replace(/"/g, '&quot;')

        form.createChild({
            tag: 'input',
            type: 'hidden',
            cls: 'x-hidden',
            name: 'values',
            value: escaped_json
        });

        form.dom.submit();

        return frame;
    }
});
