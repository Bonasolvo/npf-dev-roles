Ext.define('Xmin.util.xtypes.AddressField', {
    extend:'Xmin.util.xtypes.RelatedField',
    alias: 'widget.addressfield',

    url: '/fias/suggest_sbs/',

    getStoreConfig: function () {
        var storeCfg = this.callParent(arguments);

        Ext.apply(storeCfg.proxy.reader, {
            rootProperty: 'results',
            totalProperty: 'more'
        });

        return storeCfg;
    },

    hasNextPage: function () {
        var me = this,
            totalCount = me.store.getTotalCount();

        return totalCount == 1;
    },

    getSubmitValue: function () {
        return this.getRawValue();
    }
});