Ext.define('Xmin.util.xtypes.CustomType', {
    extend:'Ext.form.field.Text',

    alias : 'widget.xmincustomfield',
    requires  : [
        'Xmin.util.HelpImageAligner'
    ],
    validator : function(value){
        if (value !== "CustomType") {
            return true;
        }

        return gettext('This field must not be set to "CustomType".');
    },
    listeners: {
        afterrender: function () {
            Xmin.util.HelpImageAligner.align(this);
        }
    }
});