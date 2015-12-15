Ext.define('Dashboard.view.dashboard.MainMenu', {
    extend: 'Ext.tree.Panel',
    alias: 'widget.MainMenu',
    title: 'Меню',
    width: 250,
    flex: 1,
    rootVisible: false,
    store: 'MainMenu',
    id: 'main_menu_tree',
    viewConfig: {
        copy: true,
        plugins: {
           ptype: 'treeviewdragdrop',
           enableDrag: true,
           enableDrop: false,
           ddGroup: 'MainMenu2LaunchPad',
           containerScroll: true
        }
    },
    reserveScrollbar: true,
    dockedItems: [{
        id: 'main_menu_search_field',
        xtype: 'toolbar',
        dock: 'top',
        items: [{
            xtype: 'textfield',
            flex: 1,
            triggers: {
                clear_field: {
                    cls: 'x-form-clear-trigger',
                    handler: function() {
                        this.reset();
                        this.focus();
                    }
                }
            },

            //triggerCls: 'x-form-clear-trigger',
            //onTriggerClick: function () {
            //    this.reset();
            //    this.focus();
            //},


            listeners: {
                change: function (field, newVal) {
                    var tree = Ext.getCmp('main_menu_tree');
                    tree.filter(newVal);
                },
                buffer: 250
            }
        }]
    }],
    listeners: {
        afterlayout: function () {
            $('#main_menu_search_field').css('padding-top', '0px').css('padding-left', '0px');
            $('#main_menu_search_field-innerCt').css('width', $('#main_menu_search_field').css('width'));
            $('#main_menu_search_field-targetEl').css('width', $('#main_menu_search_field').css('width'));
            $('#main_menu_search_field-targetEl > div').css('width', '100%');
        },
        itemclick: function (tree, record, item, index, e, options) {
            this.changeActiveItem(record);
        }
    },
    changeActiveItem: function (record) {
        var router = Dashboard.getApplication().getController('Router'),
            add_url = record.get('add_url'),
            admin_url = record.get('admin_url');

        if (!admin_url)
            router.navigate(record.get('add_url'));
        else
            router.navigate(record.get('admin_url'));

        this.getSelectionModel().select(record);
        Ext.getCmp("breadcrumbs").setSelection(record);
    },
    filter: function (value, property, re) {
        var me = this
            , tree = me
            , matches = []                                          // array of nodes matching the search criteria
            , root = tree.getRootNode()                                // root node of the tree
            , property = property || 'text'                          // property is optional - will be set to the 'text' propert of the  treeStore record by default
            , re = re || new RegExp(value, "ig")                     // the regExp could be modified to allow for case-sensitive, starts  with, etc.
            , visibleNodes = []                                      // array of nodes matching the search criteria + each parent non-leaf  node up to root
            , viewNode;
        if (Ext.isEmpty(value)) {                                    // if the search field is empty
            me.clearFilter();
            return;
        }

        tree.expandAll();                                            // expand all nodes for the the following iterative routines

        // iterate over all nodes in the tree in order to evalute them against the search criteria
        root.cascadeBy(function (node) {
            if (node.get(property).match(re)) {                         // if the node matches the search criteria and is a leaf (could be  modified to searh non-leaf nodes)
                matches.push(node)                                  // add the node to the matches array
            }
        });

        if (me.allowParentFolders === false) {                         // if me.allowParentFolders is false (default) then remove any  non-leaf nodes from the regex match
            Ext.each(matches, function (match) {
                if (!match.isLeaf()) { Ext.Array.remove(matches, match); }
            });
        }

        Ext.each(matches, function (item, i, arr) {                 // loop through all matching leaf nodes
            root.cascadeBy(function (node) {                         // find each parent node containing the node from the matches array
                if (node.contains(item) == true) {
                    visibleNodes.push(node)                          // if it's an ancestor of the evaluated node add it to the visibleNodes  array
                }
            });
            if (me.allowParentFolders === true &&  !item.isLeaf()) {    // if me.allowParentFolders is true and the item is  a non-leaf item
                item.cascadeBy(function (node) {                    // iterate over its children and set them as visible
                    visibleNodes.push(node)
                });
            }
            visibleNodes.push(item)                                  // also add the evaluated node itself to the visibleNodes array
        });

        root.cascadeBy(function (node) {                            // finally loop to hide/show each node
            viewNode = Ext.fly(tree.getView().getNode(node));       // get the dom element assocaited with each node
            if (viewNode) {                                          // the first one is undefined ? escape it with a conditional
                viewNode.setVisibilityMode(Ext.Element.DISPLAY);     // set the visibility mode of the dom node to display (vs offsets)
                viewNode.setVisible(Ext.Array.contains(visibleNodes, node));
            }
        });
    },
    clearFilter: function () {
        var me = this
            , tree = this //.tree
            , root = tree.getRootNode();

        if (me.collapseOnClear) { tree.collapseAll(); }             // collapse the tree nodes
        root.cascadeBy(function (node) {                            // final loop to hide/show each node
            viewNode = Ext.fly(tree.getView().getNode(node));       // get the dom element assocaited with each node
            if (viewNode) {                                          // the first one is undefined ? escape it with a conditional and show  all nodes
                viewNode.show();
            }
        });
    }


});