Ext.define('Xmin.util.xtypes.HelpImage', {
    extend: 'Ext.Img',
    bodyStyle: 'margin-left: 1px',
    cls: 'help_image x-tool-img x-tool-help',

    listeners: {
        afterrender: function () {
            Ext.create('Ext.tip.ToolTip', {
                target: this.id,
                html: this.help_text
            });
        }
    }
});


