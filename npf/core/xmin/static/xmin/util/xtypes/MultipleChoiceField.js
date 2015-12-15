Ext.define('Xmin.util.xtypes.MultipleChoiceField', {
    extend: 'Ext.form.FieldContainer',
    requires: ['Ext.ux.form.ItemSelector'],
    alias: 'widget.multiplechoicefield',
    listeners: {
        beforerender: function () {
            var data_all = this.data_all;
            var data_user = this.data_user;
            var name = this.name;
            this.add({
                xtype: 'textfield',
                fieldStyle: 'text-align: left;',
                enableKeyEvents: true,
                width: 425,
                listeners: {
                    change : function(field, newValue, oldValue, options) {
                        var itemselector = this.ownerCt.items.items[1];
                        var fromStore = itemselector.fromField.boundList.getStore();
                        fromStore.clearFilter();
                        if (String(newValue).trim() != "")
                        {
                            fromStore.filterBy(function(rec, id){
                                return this.filterFunc(rec, newValue);
                            }, this);
                        }
                    }
                },
                filterFunc: function(rec, filter) {
                    var value = rec.data.text.toLowerCase();
                    var filter = filter.toLowerCase();
                    if (value.indexOf(filter) > -1) {
                        return true;
                    }
                    return false;
                }
            });
            this.add({
                xtype: 'itemselectorfield',
                name: name + '_raw',
                cls: 'x-multiple-choice-field',
                buttons: ['add', 'remove'],
                buttonsText: {
                    add: "Выбрать",
                    remove: "Удалить"
                },
                store: Ext.create('Ext.data.ArrayStore', {
                    data: data_all,
                    fields: ['value', 'text'],
                    sortInfo: {
                        field: 'value',
                        direction: 'ASC'
                    }
                }),
                displayField: 'text',
                valueField: 'value',
                value: data_user
            });
        },
        afterrender: function () {
            var left = this.items.items[1].items.items[0];
            var right = this.items.items[1].items.items[2];
            left.width = 425;
            left.height = 300;
            right.width = 425;
            right.height = 300;
        }
    },
    setValue: function (data) {
        this.data_all = data['all'];
        this.data_user = data['user'];
    }
});
