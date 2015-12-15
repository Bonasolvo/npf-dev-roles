Ext.define('Xmin.util.xtypes.TextAreaField', {
    extend: 'Ext.form.field.TextArea',
    alias: 'widget.TextAreaField',
    requires  : [
        'Xmin.util.HelpImageAligner'
    ],

    listeners: {
        afterrender: function () {
            Xmin.util.HelpImageAligner.align(this);
        }
    }
});
