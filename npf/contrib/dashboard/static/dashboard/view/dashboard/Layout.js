Ext.define('Dashboard.view.dashboard.Layout', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.Dashboard',

    layout: {
        type: 'border'
    },

    defaults: {
        collapsible: true,
        split: true
    },

    items: [
        {
            xtype: 'Tabs',
            region: 'center',
            collapsible: false
        },
        {
            region: 'west',
            layout: {
                type: 'accordion'
            },
            width: 250,
            collapsed: false,
            collapsible: true,
            collapseMode: 'mini',
            preventHeader: true,
            autoScroll: true,
            stateful: true,
            stateId: 'state_accordion',
            items: [
                {
                    xtype: 'MainMenu'
                },
                //{
                //    xtype: 'MyTasks',
                //    id: 'x-my-tasks',
                //    title: 'Мои задачи'
                //},
                {
                    xtype: 'panel',
                    title: 'Журнал действий',
                    autoScroll: true,
                    items: [
                        {
                            xtype: 'RecentActions'
                        }
                    ]
                }
            ]
        }
    ],

    dockedItems: [
        {
            xtype: 'dashboardHeader',
            dock: 'top'
        },
        {
            xtype: 'dashboardBreadcrumbsContainer',
            dock: 'top'
        }
    ]
});