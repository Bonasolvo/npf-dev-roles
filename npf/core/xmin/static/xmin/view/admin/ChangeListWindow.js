Ext.define('Xmin.view.admin.ChangeListWindow', {
    extend : 'Ext.window.Window',
    alias  : 'widget.ChangeListWindow',
    mixins: ['Xmin.view.admin.RoutableWindow'],

    require: ['Ext.grid.PagingScroller'],

    height : 400,
    width  : 600,
    layout : 'fit',

    closeAction : 'hide',

    initComponent: function() {
        this.callParent();
        this.initialConfig.title = '';
        this.add(Ext.create('Xmin.view.admin.ChangeListPanel', this.initialConfig));
    }
});
