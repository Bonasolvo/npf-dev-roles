Ext.define('Xmin.grid.CellEditor', {
    extend: 'Ext.grid.CellEditor',

    initComponent: function() {
        this.callParent();
        this.on('startedit', this.onStartEdit, this);
        this.on('complete', this.onCompleteEdit, this);
    },

    onStartEdit: function (ed, boundEl, value, eOpts) {
    },

    onCompleteEdit: function(ed, value, startValue, eOpts) {
    }
});