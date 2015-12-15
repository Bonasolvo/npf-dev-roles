Ext.define('Xmin.view.admin.ChangePasswordPanelDone', {
    extend: 'Ext.form.Panel',
    xtype: 'basic-panels',

    bodyPadding: 10,
    scrollable:true,
    width: 355,

    layout: {
        type: 'table',
        columns: 3,
        tdAttrs: { style: 'padding: 10px; vertical-align: top;' }
    },

    defaults: {
        xtype: 'panel',
        width: 200,
        height: 280,
        bodyPadding: 10
    },

    initComponent: function () {
        this.items = [
            {
                html: '<b>Пароль успешно изменен</b>'
            }
        ];

        this.callParent();
    }
});

