Ext.define('Xmin.selection.DeleteRowModel', {
    extend: 'Ext.selection.CheckboxModel',

    pruneRemoved: false,
    checkOnly: true,
    showHeaderCheckbox: false,

    selectAll: function(suppressEvent) {
        var me = this;

        if (!me.showHeaderCheckbox)
            return false;

        me.callParent(arguments);
    },

    renderer: function(value, metaData, record, rowIndex, colIndex, store, view) {
        if (record.phantom) {
            return '<div class="' + Ext.baseCSSPrefix + 'grid-row-checker phantom-record" role="presentation">&#160;</div>';
        }
        else {
            return '<div class="' + Ext.baseCSSPrefix + 'grid-row-checker" role="presentation">&#160;</div>';
        }
    },

    selectByPosition: function (position, keepExisting) {
        return false;
    },

    listeners: {
        beforeselect: function (rowmodel, record, index) {
            if (!record.phantom)
                return true;
            rowmodel.store.remove(record);
            return false;
        }
    }
});