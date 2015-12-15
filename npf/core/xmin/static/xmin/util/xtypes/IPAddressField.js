Ext.define('Xmin.util.xtypes.IPAddressField', {
    extend:'Ext.form.field.Text',
    requires  : [
        'Xmin.util.HelpImageAligner'
    ],
    alias : 'widget.IPAddressField',
    listeners: {
        afterrender: function () {
            Xmin.util.HelpImageAligner.align(this);
        }
    },
    validator : function(value){
        // Refer to ipv4_re in django/core/validators.py
        var re = /^(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}$/;
        if(re.test(value)){
            return true;
        }
        return gettext('Enter a valid IPv4 address.');
    }
});