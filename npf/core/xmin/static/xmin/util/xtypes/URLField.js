Ext.define('Xmin.util.xtypes.URLField', {
    extend: 'Ext.form.field.Text',
    alias  : 'widget.URLField',
    xtype: 'urlfield',
    labelWidth: 50,
    submitValue: false,
    requires  : [
        'Xmin.util.HelpImageAligner'
    ],

    initComponent: function(){
        this.callParent();
    },

    listeners: {
        afterrender: function() {
            var id = this.id;
            var path = this.value;

            var selector = '#' + id + '-inputWrap';
            var html = '<div id="' + id + '-link' + '" style="padding: 3px;"><a style="display:inline-block;" href="' + path + '">' + path + '</a></div>';
            $(selector).prepend(html);

            selector = '#' + id + '-inputEl';
            $(selector).hide();

            Xmin.util.HelpImageAligner.align(this);
        }
    }
});
