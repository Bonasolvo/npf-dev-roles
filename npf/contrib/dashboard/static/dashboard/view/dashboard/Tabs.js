Ext.define('Dashboard.view.dashboard.Tabs', {
    extend : 'Ext.tab.Panel',
    alias  : 'widget.Tabs',

    requires  : [
        'Xmin.util.Text'
    ],

    id: 'TabPanel',
    title: 'Закладки',

    layout: 'fit',
    tabPosition: 'bottom',
    bodyStyle: "padding: 0px;",

    tools: [
        /*
        {
            xtype: 'CloseIPSWorkflowButton'
        },
        {
            xtype: 'AppointmentWorkflowButton'
        },
        {
            xtype: 'FakeWorkflowButton'
        },*/

        {
            xtype: 'textfield',
            name: 'search',
            value: "",
            width: 200,
            listeners: {
                change: function (field, query) {
                    function _tab_search () {
                        if (query) {
                            query = query.toLowerCase();
                            $('.xmin-modellist-buttons li a').each(function () {
                                var text = $(this).text().toLowerCase();
                                if (text.indexOf(query) == -1) {
                                    $(this).attr('style', 'display: None');
                                }
                                else {
                                    $(this).removeAttr('style');
                                }
                            })
                        }
                        else {
                            $('.xmin-modellist-buttons li a').each(function () {
                                $(this).removeAttr('style');
                            })
                        }
                    }

                    var tab_title = Ext.getCmp('TabPanel').getActiveTab().title;
                    if (tab_title == 'Закладки') {
                        _tab_search();
                    }
                }
            }
        },
        {
            type: 'search',
            tooltip: 'Найти'
        },
        {
            type: 'plus',
            tooltip: 'Добавить'
        },
        {
            type: 'print',
            tooltip: 'Печать'
        },
        {
            type: 'gear',
            tooltip: 'Экспорт'
        },
        {
            type: 'help',
            tooltip: 'Справка'
        }
    ],

    items: [
        {
            xtype: 'Bookmarks',
            title: 'Закладки'
        }
    ],

    listeners: {
        afterrender: function () {
            var plus_button = $('.x-tool-img.x-tool-plus');
            plus_button.addClass('plus-button-pale');
            plus_button.click(function () {
                return false;
            });
        },
        tabchange: function (tabPanel, newCard, oldCard, eOpts) {
            // Ищем дерево значений для отображения хлебных крошек
            var result = Ext.getCmp("main_menu_tree").getStore().findBy(function (record, id) {
                if (record.raw.text.toLocaleLowerCase() == newCard.title.toLocaleLowerCase() && record.id != 'child')
                    return id;
            });

            // Если нашли, то отображает
            if (result != -1) {
                var mainMenu = Ext.getCmp("main_menu_tree");
                mainMenu.changeActiveItem(mainMenu.getStore().getAt(result));
            }
            else {
                // Иначе создаем новое дерево и сохраняем для дальнейшего использования
                var breadCrumbs = Ext.getCmp("breadcrumbs");
                var currentData = breadCrumbs.getSelection().getData();

                var currentNode = breadCrumbs.getStore().getById(currentData.parent1Id || currentData.id);
                if (currentNode == null) {
                    result = breadCrumbs.getStore().findBy(function (record, id) {
                        if (record.raw.text_child != undefined && record.raw.text_child.toLocaleLowerCase().indexOf(newCard.title.substring(0, newCard.title.indexOf(' - ')).toLocaleLowerCase()) != -1)
                            return id;
                        });
                    currentNode = breadCrumbs.getStore().getAt(result);
                }

                var childNode = currentNode.findChild('id', 'child');
                currentNode.removeChild(child);

                while(childNode) {
                    childNode.remove();
                    childNode = currentNode.findChild('id', 'child');
                }

				//workaround bug with child cache
                var dummy = currentNode.appendChild({id: 'dummy'});
                breadCrumbs.setSelection(dummy);
                dummy.remove();

                breadCrumbs.setSelection(currentNode);
                var child = currentNode.appendChild({ id: "child", text: newCard.title, leaf: 'true', parent1Id: currentNode.id });
                breadCrumbs.setSelection(child);
            }

            function processPlusButton() {
                var plus_button = $('.x-tool-img.x-tool-plus');
                plus_button.addClass('plus-button-pale');
                plus_button.click(function () {
                    return false;
                });

                var inline = false,
                    inline_add_perm = false,
                    add_perm = false;

                try {
                    inline = newCard.down('panel').activeTab;
                    inline_add_perm = newCard.down('panel').adminformInline[0].perms.add;
                }catch (e) {}

                if (inline && inline.title != 'Основные данные') {
                    if (inline_add_perm) {
                        plus_button.removeClass('plus-button-pale');
                        plus_button.off()
                    }
                } else {
                    try {
                        add_perm = newCard.initialConfig.items[0].initialConfig.xmin_admin.perms.add;
                    } catch (e) {}

                    if (add_perm) {
                        plus_button.removeClass('plus-button-pale');
                        plus_button.off()
                    }
                }
            }

            function fixTabClickEvent(obj) {
                //https://www.sencha.com/forum/showthread.php?294953-Tab-switching-bug
                obj.items.each(function (itm, idx) {
                itm.tab.on('focus', function (tab) {
                    var tabpanel = tab.up('tabpanel');
                    tabpanel.setActiveTab(idx);
                });
            });
            }

            var token = newCard.config.items == undefined ?
                '/' : newCard.config.items[0].xmin_token;
            this.setTitle(newCard.title);
            Ext.History.add(token);
            processPlusButton();
            fixTabClickEvent(this);
        }
    }
});