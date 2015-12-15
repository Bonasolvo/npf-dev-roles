Ext.define('Xmin.util.xtypes.DateField', {
    extend: 'Ext.form.field.Date',
    alias: 'widget.datefield',
    requires  : [
        'Xmin.util.HelpImageAligner'
    ],
    startDay: 1,

    listeners: {
        afterrender: function () {
            Xmin.util.HelpImageAligner.align(this);
        }
    },

    // Fix bug with datepicker in grid
    getValue: function () {
        var format = this.submitFormat || this.format,
            value = this.callParent();

        return value ? Ext.Date.format(value, format) : '';
    },

    getSubmitValue: function () {
        return this.getValue();
    }

});
