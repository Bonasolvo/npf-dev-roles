Ext.define('Xmin.view.admin.ChangePasswordPanel', {
    extend: 'Ext.form.Panel',
    xtype: 'form-register',

    bodyPadding: 10,
    scrollable: true,
    layout: 'anchor',
    frame: true,

    fieldDefaults: {
        labelAlign: 'left',
        labelWidth: 115,
        msgTarget: 'side'
    },

    items: [{
        xtype: 'fieldset',
        defaultType: 'textfield',
        bodyStyle: 'margin: 10px;',

        defaults: {
            anchor: '100%'
        },
        width: 290,

        items: [
            {
                xtype: 'panel',
                html: '<b style="color:red">Неправильный пароль</b>',
                id: 'xmin-incorrect',
                hidden: true
            },
            { id: 'xmin-old-password', allowBlank:false, fieldLabel: 'Старый пароль', name: 'old_password', inputType: 'password'},
            {
                xtype: 'panel',
                html: '<b style="color:red">Пароли не совпадают</b>',
                id: 'xmin-missmatch',
                hidden: true
            },
            { allowBlank:false, fieldLabel: 'Новый пароль', name: 'new_password', inputType: 'password' },
            { allowBlank:false, fieldLabel: 'Пароль (еще раз)', name: 'new_password_again', inputType: 'password' }
        ]
    },
        {
        xtype: 'button',
        Width: 115,
        text: 'Изменить пароль',
        disabled: true,
        formBind: true,
        handler: function() {
            Ext.get('xmin-incorrect').hide();
            Ext.get('xmin-missmatch').hide();
            var form = this.up("form").getForm(),
                formData = form.getFieldValues();
            Ext.Ajax.request({
                url: 'admin/password_change_custom/',
                method: "POST",
                headers: { 'Content-Type': 'application/json; charset=UTF-8' },
                params: Ext.JSON.encode(formData),
                success: function(response) {
                    var result = Ext.JSON.decode(response.responseText);
                    if (result.success) {
                        window.location.href='#/admin/password_change/done';
                    }
                    else {
                        if ('incorrect' in result.errors) {
                            Ext.get('xmin-incorrect').show();
                        }
                        if ('missmatch' in result.errors) {
                            Ext.get('xmin-missmatch').show();
                        }
                    }
                }
            });
        }
    }

    ]
});