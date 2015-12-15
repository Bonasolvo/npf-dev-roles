Ext.define('Xmin.view.dashboard.RecentActions', {
    // Журнал действий (отображается в главном меню)
    extend: 'Ext.view.View',
    alias: 'widget.RecentActions',

    plugins: {
        ptype: 'gridviewdragdrop',
        enableDrag: true,
        enableDrop: true,
        ddGroup: 'MainMenu2LaunchPad'
    },
    store: 'ServerEvents',
    tpl: [
        '<ul class="xmin-recent-actions-list">',
        '<tpl for=".">',
            '<li class="action {model} {action}">',
                '{[Xmin.util.Text.capfirst(values.model_name)]} ',

                '<tpl if="object_name != undefined">',
                    '<tpl if="action == \'DELETION\'">',
                        '<span class="object_name">{object_name}</span> ',
                    '<tpl else>',
                        '<a href="#{token}"><span class="object_name">{object_name}</span></a> ',
                    '</tpl>',
                '</tpl>',
                '<br />',
                '{datetime}',
            '</li>',
        '</tpl>',
        '</ul>',
        {
            label_action: function(action_label) {
                var action_texts = {
                    'ADDITION': gettext('added by'),
                    'CHANGE': gettext('changed by'),
                    'DELETION': gettext('deleted by')
                };
                return action_texts[action_label];
            },

            getUsername: function(user_id, user_name) {
                if (user_id === Xmin.settings.user.id) {
                    return gettext("me");
                }
                return user_name;
            },

            checkUsersPanelPermission: function() {
                return false;
            }
        }
    ],

    emptyText: gettext('No recent events...'),

    autoScroll: true,

    border: true,
    cls: 'xmin-recent-actions',
    itemSelector: 'li.action',

    trackOver: true,
    overItemCls: 'x-item-over',

    listeners: {
        itemmouseenter: function(view, record, item) {
            Ext.fly(item).set({'data-qtip': record.get('message')});
        }
    },

    initComponent: function() {
        this.callParent();
    }

});