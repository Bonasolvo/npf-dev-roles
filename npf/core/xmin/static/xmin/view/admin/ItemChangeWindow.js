Ext.define('Xmin.view.admin.ItemChangeWindow', {
    extend : 'Xmin.view.admin.RoutableWindow',
    alias: 'widget.ItemChangeWindow',

    initComponent: function() {
        this.callParent();
        this.initialConfig.title = '';
        this.add(Ext.create('Xmin.view.admin.ItemChangePanel', this.initialConfig));
    }
});
