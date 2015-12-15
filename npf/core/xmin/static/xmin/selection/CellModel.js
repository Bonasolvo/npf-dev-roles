Ext.define('Xmin.selection.CellModel', {
    extend: 'Ext.selection.CellModel',

    listeners: {
        beforeselect: function (rowmodel, record, index) {
            return false;
        }
    }
});
