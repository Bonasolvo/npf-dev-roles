Ext.define('Xmin.grid.header.Container', {
    override: 'Ext.grid.header.Container',

    /**
     * Returns an array of menu items to be placed into the shared menu
     * across all headers in this header container.
     * @returns {Array} menuItems
     */
    getMenuItems: function() {
        var me = this,
            menuItems = [],
            hideableColumns = me.enableColumnHide ? me.getColumnMenu(me) : null;

        if (me.sortable) {
            menuItems = [{
                itemId: 'ascItem',
                text: me.sortAscText,
                iconCls: me.menuSortAscCls,
                handler: me.onSortAscClick,
                scope: me
            },{
                itemId: 'descItem',
                text: me.sortDescText,
                iconCls: me.menuSortDescCls,
                handler: me.onSortDescClick,
                scope: me
            }, {
                itemId: 'sortClear',
                text: me.sortClearText,
                handler: me.onSortClearClick,
                scope: me
            }];
        }
        if (hideableColumns && hideableColumns.length) {
            if (me.sortable) {
                menuItems.push({
                    itemId: 'columnItemSeparator',
                    xtype: 'menuseparator'
                });
            }
            menuItems.push({
                itemId: 'columnItem',
                text: me.columnsText,
                iconCls: me.menuColsIcon,
                menu: hideableColumns,
                hideOnClick: false
            });
        }
        return menuItems;
    },

    // clear sort when clicking on item in menu
    onSortClearClick: function () {
        var me = this,
            menu = this.getMenu(),
            grid = me.up('tablepanel'),
            store = grid.store,
            activeHeader = menu.activeHeader;

        Ext.suspendLayouts();
        me.sorting = true;

        if (store.sorters.items.length > 1) {
            var sorters = [],
                activeSorters = store.sorters.items;

            for (var sorter in activeSorters) {
                if (!activeSorters.hasOwnProperty(sorter))
                    continue;

                if (activeSorters[sorter].config.property == activeHeader.dataIndex)
                    continue;

                sorters.push(activeSorters[sorter].config);
            }

            store.sort(sorters);

        } else {
            store.sorters.clear();
            store.load();
        }

        delete me.sorting;
        Ext.resumeLayouts(true);
    }
});
