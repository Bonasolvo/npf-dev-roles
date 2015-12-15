Ext.define('Xmin.data.Store', {
    extend: 'Ext.data.Store',

    constructor: function (config) {
        var me = this;

        // Fix bug with hit ajax request if set ajax proxy and set initial data
        if (config.data) {
            var proxy = config.proxy;

            if (!proxy || proxy.type != 'ajax') {
                this.callParent(arguments);
                return;
            }

            // unset proxy before load initial data
            config.proxy = undefined;

            this.callParent(arguments);

            this.on({
                scope: proxy,
                load: me.restoreProxy
            });

        } else {
            this.callParent(arguments);
        }
    },

    privates: {
        restoreProxy: function (store, records, successful, eOpts, e) {
            if (store.proxy.type == e.scope.type)
                return;

            // set proxy after load initial data
            store.setProxy(e.scope);
        }
    }

});