Ext.define('Xmin.util.xtypes.RelatedField', {
    // Поле c foreign key
    extend: 'Ext.form.field.ComboBox',
    alias: 'widget.relatedfield',

    requires  : [
        'Xmin.util.HelpImageAligner'
    ],

    minChars: 2,

    queryMode: 'remote',
    queryParam: 'term',
    displayField: 'text',
    valueField: 'id',
    editable: true,
    forceSelection: false,
    typeAhead: true,

    config: {
        url: '/xmin/data/suggest_items/',
        model: '',
        data: []
    },

    initComponent: function () {
        var storeCfg = this.getStoreConfig();

        Ext.apply(this, {
            store: Ext.create('Xmin.data.Store', storeCfg),
            bufferStore: Ext.create('Xmin.data.Store', storeCfg)
        });

        this.callParent();
    },

    getStoreConfig: function () {
        var url = this.suggest_url ? '/xmin/data' + this.suggest_url : this.url;
        var storeCfg = {
            data: this.initialConfig.data,
            fields: [this.valueField, this.displayField],
            proxy: {
                type: 'ajax',
                url: url,
                startParam: undefined,
                limitParam: undefined,
                extraParams: {
                    suggest_context: this.name
                },
                reader: {
                    type: 'json',
                    rootProperty: 'data',
                    totalProperty: 'total'
                }
            }
        };

        if (this.model) {
            storeCfg.proxy.extraParams.model = this.model;
        }

        return storeCfg;
    },

    createPicker: function() {
        var me = this,
            picker = this.callParent(arguments);

        me.mon(picker, {
            render: function() {
                picker.on({
                    scope: {
                        me: me,
                        listEl: Ext.get(picker.id + '-listEl').dom,
                        pickerEl: picker.getEl().dom
                    },
                    scroll: me.onScroll
                });
            }
        });

        return picker;
    },

    onScroll: function(picker, x, y, eOpts) {
        // При прокрутке списка, подгружаем данные из хранилища
        var me = eOpts.scope.me,
            scrollHeight = eOpts.scope.listEl.scrollHeight,
            clientHeight = eOpts.scope.pickerEl.clientHeight;

        if (y + 1 >= scrollHeight - clientHeight) {
            me.loadNextPage();
        }
    },

    hasNextPage: function () {
        var me = this,
            count = me.store.getCount(),
            totalCount = me.store.getTotalCount();

        return count < totalCount;
    },

    loadNextPage: function() {
        var me = this,
            picker = me.getPicker();

        if (!me.hasNextPage())
            return;

        picker.setLoading(true);

        me.bufferStore.proxy.extraParams[me.queryParam] = me.inputEl.getValue();

        me.bufferStore.loadPage(me.store.currentPage + 1, {
            scope: me,
            callback: function(records, operation, success) {
                picker.setLoading(false);

                if (!success) {
                    return;
                }

                me.store.add(records);
                me.store.currentPage += 1;
            }
        });
    },

    getValue: function () {
        return this.value;
    },

    listeners: {
        afterrender: function () {
            Xmin.util.HelpImageAligner.align(this);
        },

        beforequery: function(qe) {
            qe.query = qe.combo.inputEl.getValue();

            if (qe.combo.lastQuery != qe.query) {
                qe.combo.store.loadRecords([], false);
                qe.combo.store.currentPage = 1;
                delete qe.combo.lastQuery;
            }
        }
    },

    privates: {
        bufferStore: null
    }

});