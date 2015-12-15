Ext.define('Xmin.grid.filters.filter.Address', {
    extend: 'Ext.grid.filters.filter.SingleFilter',
    alias: 'grid.filter.address',
    requires: ['Xmin.util.xtypes.AddressField'],

    type: 'address',
    operator: 'like',
    url: '',

    itemDefaults: {
        xtype: 'addressfield',
        url: '/fias/suggest_sbs/',
        enableKeyEvents: true,
        width: 350
    },

    createMenu: function () {
        var me = this,
            config;

        me.callParent();

        config = Ext.apply({url: this.url}, me.getItemDefaults());

        // Добавляем поле ввода типа "addressfield"
        // c заданными в "itemDefaults" настройками
        me.inputItem = me.menu.add(config);

        // Добавляем обработчики событий
        me.inputItem.on({
            scope: me,
            change: me.onValueChange,
            keypress: me.onKeyPress,
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

    getValue: function () {
        var me = this;
        return me.value;
    },

    activateMenu: function () {
        this.inputItem.setValue(this.filter.getValue());
    },

    onKeyPress: function (field, e, eOpts) {
        var me = this,
            rawValue = field.getRawValue();

        if (e.getKey() === e.RETURN && me.getValue() != rawValue) {
            me.apply(rawValue);
        }
    },

    onValueChange: function (field, newValue, oldValue, eOpts) {
        var me = this;
        if (this.inp)
        {
            this.inp = false;
            return;
        }
        me.apply(field.getRawValue());
    },

    apply: function (value) {

        var me = this,
            // Number of milliseconds to wait after user interaction to fire an update.
            // Only supported by filters: 'list', 'numeric', and 'string'. Defaults to 500.
            updateBuffer = me.updateBuffer;

        if (!value) return;

        this.inp = true;

        if (updateBuffer) {
            me.task.delay(1000, null, null, [value]);
        } else {
            me.setValue(value);
        }
    }
});