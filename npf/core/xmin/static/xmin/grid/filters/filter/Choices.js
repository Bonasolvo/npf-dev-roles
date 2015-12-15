Ext.define('Xmin.grid.filters.filter.Choices', {
    extend: 'Ext.grid.filters.filter.SingleFilter',
    alias: 'grid.filter.choices',
    requires: ['Xmin.util.xtypes.ChoicesField'],

    type: 'choices',
    operator: 'eq',
    choices: [],

    itemDefaults: {
        xtype: 'choices',
        width: 300
    },

    createMenu: function () {
        var me = this,
            config;

        me.callParent();

        config = Ext.apply({choices: this.choices}, me.getItemDefaults());

        me.inputItem = me.menu.add(config);
        me.setValue('all');

        me.inputItem.on({
            scope: me,
            change: me.onValueChange,
            el: {
                click: function(e) {
                    e.stopPropagation();
                }
            }
        });
    },

    setValue: function (value) {
        var me = this;

        if (me.inputItem) {
            me.inputItem.setValue(value);
        }

        me.filter.setValue(value);

        if (value && value != 'all' && me.active) {
            me.value = value;
            me.updateStoreFilter();
        } else {
            me.setActive(value != 'all');
        }
    },

    activateMenu: function () {
        this.inputItem.setValue(this.filter.getValue());
    },

    onValueChange: function (field, newValue, oldValue, eOpts) {
        var me = this,
            // Number of milliseconds to wait after user interaction to fire an update.
            // Only supported by filters: 'list', 'numeric', and 'string'. Defaults to 500.
            updateBuffer = me.updateBuffer;

        if (updateBuffer) {
            me.task.delay(updateBuffer, null, null, [me.getValue(field)]);
        } else {
            me.setValue(me.getValue(field));
        }
    }
});