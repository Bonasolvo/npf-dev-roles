Ext.define('Xmin.grid.filters.filter.Related', {
    extend: 'Ext.grid.filters.filter.SingleFilter',
    alias: 'grid.filter.related',
    requires: ['Xmin.util.xtypes.RelatedField'],

    type: 'related',
    operator: 'eq',
    model: '',

    itemDefaults: {
        xtype: 'relatedfield',
        width: 300
    },

    createMenu: function () {
        var me = this,
            config;

        me.callParent();

        config = Ext.apply({model: this.model}, me.getItemDefaults());

        me.inputItem = me.menu.add(config);

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

        if (value && me.active) {
            me.value = value;
            me.updateStoreFilter();
        } else {
            me.setActive(!!value);
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