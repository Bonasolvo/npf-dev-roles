Ext.define('Xmin.util.xtypes.TextField', {
    extend: 'Ext.form.field.Text',
    alias: 'widget.TextField',
    requires  : [
        'Xmin.util.HelpImageAligner'
    ],

    listeners: {
        afterrender: function () {
            Xmin.util.HelpImageAligner.align(this);
        }
    }
});
