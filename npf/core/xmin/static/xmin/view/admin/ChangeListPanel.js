Ext.ns('Ext.ux.state');

// LacalStorage используется для хранения информации о состоянии колонок таблиц

Ext.ux.state.LocalStorage = function(config) {
    Ext.ux.state.LocalStorage.superclass.constructor.call(this);
    Ext.apply(this, config);
    // get all items from localStorage
    this.state = this.readLocalStorage();
};

Ext.extend(Ext.ux.state.LocalStorage, Ext.state.Provider, {
    namePrefix: 'ys-',

    set: function(name, value) {
        if (typeof value == "undefined" || value === null) {
            this.clear(name);
            return;
        }
        // write to localStorage
        localStorage.setItem(this.namePrefix + name, this.encodeValue(value));
        Ext.ux.state.LocalStorage.superclass.set.call(this, name, value);
    },

    clear: function(name) {
        localStorage.removeItem(this.namePrefix + name);
        Ext.ux.state.LocalStorage.superclass.clear.call(this, name);
    },

    readLocalStorage: function() {
        var data = {};
        for (var i = 0; i <= localStorage.length - 1; i++) {
            var name = localStorage.key(i);
            if (name && name.substring(0, this.namePrefix.length) == this.namePrefix) {
                data[name.substr(this.namePrefix.length)] = this.decodeValue(localStorage.getItem(name));
            }
        }
        return data;
    }
});

if (window.localStorage) {
    Ext.state.Manager.setProvider(new Ext.ux.state.LocalStorage({namePrefix:'my-'}))
}

Ext.define('Xmin.view.admin.ChangeListPanel', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.ChangeListPanel',
    xtype: 'changeListPanel',

    require: [
        'Ext.grid.PagingScroller',
        'Xmin.grid.CellEditor',
        'Xmin.data.Store',
        'Xmin.selection.DeleteRowModel',
        'Xmin.selection.CellModel',
        'Ext.state.*'
    ],

    uses: [
//        'Xmin.grid.header.Container'
    ],

    itemId: 'ChangeListGrid',
    plugins: ['gridfilters'],
    border: false,
    multiColumnSort: true,
    columnLines: true,
    stateful: true,
    prefix: '',
    keyFields: [],
    editable: false,
    changedRecordsList: {},
    markedCellsList: [],

    xtypeColumn: 'xtype',
    xtypeEditorColumns: ['first_value', 'second_value'],

    listeners: {
        beforestatesave: function (a, b) {
            b.storeState = {};
        },
        selectionchange: function () {
            this.updateSelectionText();
        },

        itemclick: function () {
            this.updateSelectionText();
        },
    },

    initComponent: function() {
        var me = this,
            store, grid, model_fields,
            fields_by_name = {},
            config = me.initialConfig,
            token = config.xmin_model.admin_url,
            store_id = '/store/buffered' + token;

        me.isInline = me.prefix != '';
        me.editable = me.isInline; // todo temprary hack

        me.editing = Ext.create('Ext.grid.plugin.CellEditing', { clicksToEdit: 1 });
        me.plugins = ["gridfilters", me.editing];
        if (me.prefix) {
            var raw_grid_name = token.split('/'),
                grid_name = Ext.String.format('{0}/{1}/{2}', raw_grid_name[1], raw_grid_name[2], raw_grid_name[3]),
                inline_name = config.xmin_config.class.toLowerCase();

            me.stateId = Ext.String.format('/state/grid/{0}/{1}/', grid_name, inline_name);

        } else {
            var grid_name = token; //this.xmin_token;
            me.stateId = '/state/grid' + grid_name;
        }

        if (me.prefix && (config.xmin_config.perms.delete || me.xmin_config.perms.add)) {
            me.selModel = Ext.create('Xmin.selection.DeleteRowModel');
        } else if (config.xmin_model.actions) {
            me.selModel = Ext.create('Xmin.selection.DeleteRowModel', { showHeaderCheckbox: true });
        } else {
            me.selModel = Ext.create('Xmin.selection.CellModel');
        }

        // Create model fields config
        model_fields = [{
            xtype: 'field',
            name: '__str__'
        }];

        for (var i = 0; i < config.xmin_model.fields.length; i++) {
            var field = config.xmin_model.fields[i];

            model_fields.push({
                xtype : 'field',
                name  : field.name
            });

            fields_by_name[field.name] = field;
        }

        // Create store
        store = Ext.create('Xmin.data.Store', {
            storeId: store_id,
            data: config.xmin_admin.data,
            fields: model_fields,
            pageSize: config.xmin_model.list_per_page,
            remoteFilter: true,
            remoteSort: true,
            proxy: {
                type: 'ajax',
                url: Xmin.settings.urls.xmin_data + token,
                startParam: undefined,
                limitParam: undefined,
                reader: {
                    type: 'json',
                    rootProperty: 'data',
                    totalProperty: 'total'
                }
            }
        });

        actions_store = Ext.create('Ext.data.ArrayStore', {
            storeId: '/store/actions' + token,
            fields: [
                {name: 'name', type: 'auto'},
                {name: 'text', type: 'auto'},
                {name: 'items', type: 'auto'},
            ],
            proxy: {
                type: 'ajax',
                startParam: undefined,
                limitParam: undefined,
                pageParam: undefined,
                url: Xmin.settings.urls.xmin_data + token + 'actions',
                reader: {
                    type: 'json',
                }
            }
        });

        var ActionsMenu = Ext.create('Ext.menu.Menu');

        if (!me.isInline)
            var pagingToolbar = Ext.create('Ext.PagingToolbar', {
                store: store,
                displayInfo: true,
                border: false,
                items: [
                    '-',
                    {
                        xtype: 'tbtext',
                        name: 'status_field',
                        text: '&nbsp;'
                    },
                    {
                        xtype: 'button',
                        text: 'Действие',
                        name: 'actions_menu',
                        menu: ActionsMenu
                    }
                ]
            });

        Ext.apply(me, {
            columns: me.prepareColumns(),
            store: store,
            bbar: pagingToolbar
        });

        me.callParent();

        store.load();
        actions_store.load();

        if (!me.isInline) {
            var actions_button = this.down('[name="actions_menu"]'),
                status_field = this.down('[name="status_field"]'),
                that = this;

            store.on("load", function (store, records, successful, eOpts) {
                that.updateSelectionText();
            });

            actions_store.on("load", function (store, records, successful, eOpts) {
                me.setActions(store, ActionsMenu);
            });
        }
    },

    setActions: function (store, menu) {
        menu.removeAll();
        store.each(function () {
            item = this
            if (item.get('name')) {
                var element = {
                    text: item.get('text'),
                    name: item.get('name')
                };
                if (item.get('items')) {
                    element['menu'] = {xtype: 'menu', items: item.get('items')};
                }
                menu.add(element)
            }
        })
    },

    addNewRow: function () {
        //TODO optimize it!
        var columns = Ext.Array.pluck(this.headerCt.getGridColumns(), 'dataIndex'),
            record = {};

        for (var column in columns) {
            if (!columns.hasOwnProperty(column))
                continue;

            column = columns[column];

            if (column == "")
                continue;

            record[column] = null;
        }

        this.editing.cancelEdit();
        this.getStore().insert(0, record);
        this.editing.startEditByPosition({ row: 0, column: 1 }); // TODO incorect init datetetime picker
    },

    getValues: function() {
        var me = this,
            config = me.initialConfig, store = me.getStore(),
            values = {}, totalFormsIndex = 0, initialFormsIndex = 0, fieldName,
            totalForms = Ext.String.format('{0}-TOTAL_FORMS', me.prefix),
            initialForms = Ext.String.format('{0}-INITIAL_FORMS', me.prefix),
            removedRecords = me.getSelectionModel().getSelection() || [],
            removedRecordsIDs = [],
            updatedRecords = config.xmin_config.commit_unchanged_records ?
                store.getRange() : store.getUpdatedRecords(),
            newRecords = store.getNewRecords(),
            modifiedRecords = Ext.Array.merge(updatedRecords, newRecords);

        // init selected records IDs for delete
        for (var record in removedRecords) {
            if (!removedRecords.hasOwnProperty(record))
                continue;

            record = removedRecords[record];

            removedRecordsIDs.push(record.id);

            if (record.phantom)
                continue;

            for (var keyField in me.keyFields) {
                if (!me.keyFields.hasOwnProperty(keyField))
                    continue;

                keyField = me.keyFields[keyField];

                fieldName = Ext.String.format('{0}-{1}-{2}', me.prefix, totalFormsIndex, keyField);
                values[fieldName] = record.data[keyField];
            }

            fieldName = Ext.String.format('{0}-{1}-DELETE', me.prefix, totalFormsIndex);
            values[fieldName] = 'on';

            totalFormsIndex++;
            initialFormsIndex++;
        }

        // get modified records
        for (record in modifiedRecords) {
            if (!modifiedRecords.hasOwnProperty(record))
                continue;

            record = modifiedRecords[record];

            if (Ext.Array.contains(removedRecordsIDs, record.id))
                continue;

            me.changedRecordsList[Ext.String.format('{0}-{1}', me.prefix, totalFormsIndex)] = record;

            if (!record.phantom)
                initialFormsIndex++;

            // prepare changed record values
            for (var field in record.data) {
                if (!record.data.hasOwnProperty(field))
                    continue;

                fieldName = Ext.String.format('{0}-{1}-{2}', me.prefix, totalFormsIndex, field);

                if (record.phantom) {
                    // Skip key fields
                    if (Ext.Array.contains(me.keyFields, field))
                        continue;

                } else {

                    for (keyField in me.keyFields) {
                        if (!me.keyFields.hasOwnProperty(keyField))
                            continue;

                        keyField = me.keyFields[keyField];
                        keyFieldName = Ext.String.format('{0}-{1}-{2}', me.prefix, totalFormsIndex, keyField);

                        values[keyFieldName] = record.data[keyField];
                    }
                }

                if (!Ext.Array.contains(me.keyFields, field)) {
                    if (!me.xmin_model.fieldsArr[field])
                        continue;

                    if (me.xmin_model.fieldsArr[field].field_class == 'django.db.models.fields.DateTimeField') {
                        var datetime = record.data[field];

                        if (!datetime) {
                            values[Ext.String.format('{0}_0', fieldName)] = null;
                            values[Ext.String.format('{0}_1', fieldName)] = null;
                            continue;
                        }

                        datetime = datetime.split(' ');
                        values[Ext.String.format('{0}_0', fieldName)] = datetime[0] ? datetime[0] : null;
                        values[Ext.String.format('{0}_1', fieldName)] = datetime[1] ? datetime[1].split('+')[0] : null;

                        continue;
                    }
                }

                values[fieldName] = record.data[field];
            }

            totalFormsIndex++;
        }

        // update management form
        if (modifiedRecords.length > 0 || removedRecords.length > 0) {
            values[totalForms] = totalFormsIndex;
            values[initialForms] = initialFormsIndex;
        } else {
            values[totalForms] = 0;
            values[initialForms] = 0;
            return values;
        }

        return values;
    },

    markInvalid: function(errors) {

        var expr = new RegExp('(.*)-(.*)-(.*)'),
            store = this.getStore(),
            view = this.getView(),
            columnIndices = Ext.Array.pluck(this.headerCt.getGridColumns(), 'dataIndex'),
            record, rowIndex, columnIndex, cell;

        this.cleanErrors();

        for (var error in errors) {
            if (!errors.hasOwnProperty(error))
                continue;

            var matches = error.match(expr);

            if (!matches)
                continue;

            var prefix = matches[1],
                index = matches[2],
                field = matches[3];

            if (prefix != this.prefix)
                continue;

            // TODO optimize get record and rowIndex for iterate fields!
            record = this.changedRecordsList[Ext.String.format('{0}-{1}', prefix, index)];
            rowIndex = store.indexOf(record);

            columnIndex = Ext.Array.indexOf(columnIndices, field);
            cell = view.getCellByPosition({row: rowIndex, column: columnIndex});

            cell.addCls('x-grid-cell-error');
            cell.set({'data-errorqtip': errors[error].join('<br/>')});

            this.markedCellsList.push(cell);
        }

        this.changedRecordsList = {};
    },

    commitChanges: function () {
        var store = this.getStore(),
            removedRecords = this.getSelectionModel().getSelection() || [];

        //TODO update primary key records after commit!

        this.cleanErrors();
        store.remove(removedRecords);
        store.commitChanges();
    },

    cleanErrors: function () {

        this.editing.cancelEdit();

        for (var cell in this.markedCellsList) {
            if (!this.markedCellsList.hasOwnProperty(cell))
                continue;

            cell = this.markedCellsList[cell];
            cell.removeCls("x-grid-cell-error");
            cell.set({'data-errorqtip': ''});
        }

        this.markedCellsList = [];
    },

    privates: {
        getEditorByXtypeColumn: function (column) {
            var me = this;

            return function (record) {
                var fieldCfg = Ext.JSON.decode(record.get(me.xtypeColumn));

                if (Ext.Array.contains(['relatedfield'], fieldCfg.xtype)) {
                    Ext.apply(fieldCfg, {
                        data: [
                            [record.get(column.dataIndex), record.get(Ext.String.format('{0}_display', column.dataIndex))]
                        ]
                    });
                } else if ('addressfield' == fieldCfg.xtype) {
                    Ext.apply(fieldCfg, {
                        data: [
                            [record.get(column.dataIndex), record.get(column.dataIndex)]
                        ]
                    });
                }

                return Ext.create('Ext.grid.CellEditor', {
                    field: fieldCfg,
                    getValue: function() {
                        var me = this;

                        if (me.field.xtype == 'addressfield') {
                            return me.field.getRawValue();
                        }

                        return me.field.getValue();
                    },
                    listeners: {
                       complete: function (editor, value, startValue, eOpts) {
                           if ('relatedfield' == editor.field.xtype) {
                               record.set(Ext.String.format('{0}_display', column.dataIndex), editor.field.getRawValue());
                           }
                       }
                   }
                });
            }
        },

        getRendererByXtypeColumn: function (column) {
            var me = this;

            return function (value, metaData, record) {
                var fieldCfg = Ext.JSON.decode(record.get(me.xtypeColumn));

                if (fieldCfg.xtype == 'datefield') {
                    return Ext.util.Format.date(value, django.formats['DATE_FORMAT']);
                }

                if (Ext.Array.contains(['choices', 'relatedfield'], fieldCfg.xtype)) {
                    var fieldName = Ext.String.format('{0}_display', column.dataIndex);
                    return record.get(fieldName);
                } else if ('addressfield' == fieldCfg.xtype) {
                    return record.get(column.dataIndex);
                }

                return value;
            }
        },

        prepareColumns: function (cols, pref) {
            var me = this, columnId,
                columns = typeof cols == 'undefined' ? me.initialConfig.xmin_model.columns : cols;

            for (var column in columns) {
                if (!columns.hasOwnProperty(column))
                    continue;

                columnId = column;
                column = columns[column];

                column.stateful = true;
                if (typeof pref == 'undefined')
                    column.stateId = Ext.String.format('{0}column/{1}/', me.stateId, columnId);
                else column.stateId = Ext.String.format(pref + '{0}/', columnId);

                if (typeof column['columns'] != 'undefined') me.prepareColumns(column['columns'], column.stateId);

                if (column.field || !Ext.Array.contains(me.xtypeEditorColumns, column.dataIndex)) {
                    continue;
                }

                column.getEditor = me.getEditorByXtypeColumn(column);
                column.renderer = me.getRendererByXtypeColumn(column);

            }

            return columns;
        },

        updateSelectionText: function () {
            var count = this.store.getTotalCount(),
                selected_count = this.getSelectionModel().getCount();

            var status_field = this.down('[name="status_field"]');
            status_field.setText(interpolate(
                ngettext('Выбрано записей: %(sel)s из %(cnt)s', 'Выбрано записей: %(sel)s из %(cnt)s', selected_count),
                {sel: selected_count, cnt: count}, true));

        }
    }
});
