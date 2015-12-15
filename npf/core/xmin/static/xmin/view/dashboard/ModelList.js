Ext.define('Xmin.view.dashboard.ModelList', {
    // Список моделей отдельного приложения в главном меню
    extend : 'Ext.view.View',
    alias  : 'widget.ModelList',

    requires  : [
        'Xmin.util.Text'
    ],

    deferInitialRefresh: false,

    tpl  : Ext.create('Ext.XTemplate',
        '<ul class="xmin-modellist-buttons">',
        '<tpl for=".">',
            '<li>',
                '<a class="{model}">{[Xmin.util.Text.capfirst(values.verbose_name_plural)]}</a>',
            '</li>',
        '</tpl>',
        '</ul>'
    ),

    plugins : [
        Ext.create('Ext.ux.DataView.Animated', {
            duration  : 250,
            idProperty: 'model'
        })
    ],

    cls: 'xmin-modellist',
    itemSelector: 'a',
    autoScroll  : true,

    initComponent: function(){
        var that = this;

        Ext.applyIf(that, {
            store : Ext.create('Ext.data.Store', {
                fields : [
                    'app',
                    'model',
                    'verbose_name_plural',
                    'add_url',
                    'admin_url',
                    'perms'
                ],
                data : that.initialConfig.xmin_data
            })
        });

        that.callParent(arguments);
    }
});