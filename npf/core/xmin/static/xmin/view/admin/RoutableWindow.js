Ext.define('Xmin.view.admin.RoutableWindow', {
    extend : 'Ext.window.Window',

    height : 400,
    width  : 600,
    minWidth: 600,
    minHeight: 200,
    layout : 'fit',

    closeAction : 'hide',

    listeners: {
        activate: function(window, e, eOpts){
            Ext.util.History.add(window.xmin_token);
        },

        deactivate: function(window, e, eOpts){
            Ext.util.History.add('');
        }
    },

    initComponent: function(){
        this.callParent();
    }
});
