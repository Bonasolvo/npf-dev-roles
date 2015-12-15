Ext.define('Xmin.view.admin.ChangeListPanelTree', {
    // Представление для древовидных списков
    // Данный функуционал скрыт к текущей реализации т.к. не закончен

    extend: 'Ext.tree.Panel',
    alias: 'widget.ChangeListTreePanel',

    requires: [
        'Xmin.data.Store',
        'Ext.data.*',
        'Ext.grid.*',
        'Ext.tree.*',
        'Ext.ux.CheckColumn'
    ],
    viewConfig: {
        toggleOnDblClick: false,
        plugins: {
            ptype: 'treeviewdragdrop',
            containerScroll: true
        }
    },
    xtype: 'tree-grid',
    itemId: 'ChangeListTreeGrid',
    reserveScrollbar: true,
    useArrows: true,
    rootVisible: false,
    multiSelect: true,
    singleExpand: false,
    rowLines: true,

    initComponent: function() {

        function _create_store () {
            return Ext.data.TreeStore({
                remoteSort: true,
                proxy: {
                    type: 'ajax',
                    url: Xmin.settings.urls.xmin_data + token
                },
                listeners: {
                    sort: function () {
                        var tree_grid = Ext.getCmp(grid_id);
                        var view = tree_grid.getScrollTarget();
                        view.scrollTo(0, tree_grid.scroll_position);
                    }
                }
            });
        }

        function _create_columns () {
        var filterTypeMap = {
            'django.db.models.fields.AutoField': 'numeric',
            'django.db.models.fields.CharField': 'string',
            'django.db.models.fields.TextField': 'string',
            'django.db.models.fields.DateTimeField': 'date'
        };

        var fields_by_name = {};
        for (var i = 0; i < config.xmin_model.fields.length; i++) {
            var field = config.xmin_model.fields[i];
            fields_by_name[field.name] = field;
        }

        var columns = [];
        for (var i = config.xmin_model.list_display.length - 1; i >= 0; i--){
            var display_field_name = config.xmin_model.list_display[i],
                field = fields_by_name[display_field_name];

            if(field !== undefined) {
                var editor = null, filter_type = filterTypeMap[field.field_class],
                    field_config = field.editable && this.editable ?
                        Xmin.util.xtypes.Factory.get_form_field_config(field) : null;

                if (field_config) {
                    field_config.fieldLabel = null;
                    editor = Ext.widget(field_config.xtype, field_config);
                }

                if (filter_type == undefined)
                    filter_type = 'string';

                var columnRenderer = null;

                if (field_config && Ext.Array.contains(['combo', 'relatedfield', 'select2', 'addressfield',
                            'AddressWithHouseField'], field_config.xtype)) {

                    columnRenderer = this.getColumnRenderer(editor);

                } else if (field_config && field_config.xtype == 'datefield') {

                    columnRenderer = Ext.util.Format.dateRenderer(editor.format);
                }

                columns.push({
                    dataIndex: field.name,
                    text: Xmin.util.Text.capfirst(field.verbose_name),
                    filter: filter_type,
                    flex: 1,
                    editor: editor,
                    renderer: columnRenderer
                });
                }
            }
        columns.reverse();
        columns[0]['xtype'] = 'treecolumn';
        return columns;
        }

        function _create_actions_buttons () {
            var actions = [];
            for (var i = 0; i < config.xmin_model.actions.length; i++) {
                var action = config.xmin_model.actions[i];
                if (action[0]) {
                    actions.push({text: action[1], name: action[0]});
                }
            }
            return actions;
        }

        var config = this.initialConfig;
        this.id = Xmin.util.CompileId.replace_slashes(config.xmin_token);
        var grid_id = this.id;
        var token = config.xmin_model.admin_url;
        this.store = _create_store();
        var actions = _create_actions_buttons();
        this.columns = _create_columns();

        this.bbar = [{
                        xtype: 'button',
                        text: 'Действие',
                        name: 'actions_menu',
                        menu: actions
                    }];
        this.selModel = Ext.create('Ext.selection.CheckboxModel', {
            mode: "MULTI",
            pruneRemoved: false,
            checkOnly: true
        });
        this.callParent();
    },
    listeners: {
        afterrender: function () {
            var grid_id = this.id;
            $(Ext.getCmp(grid_id).ownerCt.body.dom).find( "div.x-column-header-inner").on('click', function () {
                var tree_grid = Ext.getCmp(grid_id);
                var view = tree_grid.getScrollTarget();
                tree_grid.scroll_position = view.getScrollY();
            })
        },
        itemmove: function (node, old_parent, new_parent, unknown_int, unknown_obj) {
            Ext.Ajax.request({
                url: 'dict/send_node_move',
                method: "post",
                params: {
                    'node_id': node.id,
                    'new_parent_id': new_parent.id,
                    'model': this.xmin_model.model_name
                },
                success: function (response) {}})
        }
    }
});