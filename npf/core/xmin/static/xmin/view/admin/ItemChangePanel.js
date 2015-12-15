Ext.define('Xmin.view.admin.ItemChangePanel', {
    extend: 'Ext.tab.Panel',
    alias: 'widget.ItemChangePanel',
    xtype: 'itemChangePanel',

    requires: ['Xmin.util.xtypes.Factory', 'Xmin.util.Messages', 'Xmin.view.admin.ChangeListPanel'],

    dockedItems: [{
        xtype: 'toolbar',
        dock: 'bottom',
        border: false,
        items: []
    }],

    border: false,

    initComponent: function() {
        var that = this;
        this.callParent();

        this.perms = this.initialConfig.xmin_admin.perms;
        this.token = this.initialConfig.xmin_token;

        this.adminform = this.initialConfig.xmin_admin.adminform;
        this.adminformInline = this.initialConfig.xmin_admin.adminform_inline;

        this.initToolbar();
        this.initMainForm();
    },

    listeners: {
        afterrender: function () {
            // Скрываем вкладку инлайн формы, если она одна
            var panel_id = this.tabBar.id;
            var selector = '#' + panel_id + '-targetEl';
            if ($(selector + ' a').length == 1) {
                selector = '#' + panel_id + '-innerCt';
                $(selector).css('display', 'none');
            }
        },
        tabchange: function (tabPanel, newCard, oldCard, eOpts) {
            var plus_button = $('.x-tool-img.x-tool-plus');
            plus_button.addClass('plus-button-pale');
            plus_button.click(function () {
                return false;
            });

            // Проверяем права на добавление записей и при их наличии разблокируем кнопку "+"
            var add_perm = false;
            if (newCard.title == 'Основные данные') {
                try {
                    add_perm = this.perms.add;
                } catch (e) {}
            } else {
                try {
                    add_perm = this.adminformInline[0].perms.add;
                } catch (e) {}
            }

            if (add_perm) {
                plus_button.removeClass('plus-button-pale');
                plus_button.off()
            }
        }
    },

    initToolbar: function () {
        // Настройка тулбара в зависимости от текущих разрешений пользователя.
        if (!this.perms.delete && !this.perms.add && !this.perms.change)
            return;

        this.dockedItems.items[0].add({ xtype : 'tbfill' });

        if (this.perms.delete)
            this.dockedItems.items[0].add({
                xtype: 'button',
                text: 'Удалить',
                name: 'delete_button'
            });

        if (this.perms.change || this.perms.add)
            this.dockedItems.items[0].add([
                {
                    xtype: 'button',
                    text: 'Сохранить и продолжить редактирование',
                    name: 'save_and_edit_button'
                },
                {
                    xtype: 'button',
                    text: 'Сохранить',
                    name: 'save_button'
                }
            ]);
    },

    initMainForm: function () {
        var that = this;

        function initChangeForm(adminform) {
            if (adminform.management_form) {
                var managementForm = { xtype: 'form' };

                if (adminform.fieldsets) {
                    var panel = that.mainForm.add({
                        xtype: 'panel',
                        layout: 'auto',
                        margin: '5 0 0 0',
                        border: false,
                        title: adminform.verbose_name_plural
                    });

                    managementForm = panel.add(managementForm);
                } else {
                    managementForm = that.mainForm.add(managementForm);
                }

                var totalForms = adminform.management_form.TOTAL_FORMS;

                for (var attrname in adminform.management_form) {
                    if (!adminform.management_form.hasOwnProperty(attrname))
                        continue;

                    var field_name = Ext.String.format('{0}-{1}', adminform.prefix, attrname),
                        field_value = adminform.management_form[attrname];

                    managementForm.add(Xmin.util.xtypes.Factory.get_form_field_config_hidden(field_name, field_value));
                }

                if (adminform.data.length == 0)
                    adminform.data = new Array(totalForms);

            } else {
                adminform.data = [adminform.data];
            }

            if (!adminform.fieldsets)
                return;

            Ext.suspendLayouts();


            for (var index = 0; index < adminform.data.length; index++) {
                for (var fieldset in adminform.fieldsets) {
                    if (!adminform.fieldsets.hasOwnProperty(fieldset))
                        continue;

                    fieldset = adminform.fieldsets[fieldset];
                    var title = fieldset[0],
                        opts = fieldset[1],
                        classes = fieldset[1].classes ? fieldset[1].classes : [],
                        data = adminform.data[index],
                        widget;

                    var form = that.mainForm.add({
                        xtype: 'form',
                        layout: 'form',
                        margin: adminform.data.length == 1 ? '0 0 5 0' : '0 0 0 0',
                        border: true,
                        title: title,
                        collapsible: Ext.Array.contains(classes, 'collapse')
                    });

                    for (var field in opts.fields) {
                        if (!opts.fields.hasOwnProperty(field))
                            continue;

                        var fieldName = opts.fields[field];
                        field = adminform.fields[fieldName];

                        field.form_model = adminform.model;

                        field.name = adminform.prefix ?
                            Ext.String.format('{0}-{1}-{2}', adminform.prefix, index, fieldName) : fieldName;

                        widget = Ext.widget(Xmin.util.xtypes.Factory.get_form_field_config(field));

                        widget = that.setWidgetValue(widget, data, field, adminform);

                        form.add(widget);
                    }

                    if (data && adminform.hidden_fields) {
                        for (field in adminform.hidden_fields) {
                            if (!adminform.hidden_fields.hasOwnProperty(field))
                                continue;

                            fieldName = Ext.String.format('{0}-{1}-{2}',
                                adminform.prefix, index, adminform.hidden_fields[field]);

                            widget = Ext.widget(Xmin.util.xtypes.Factory.get_form_field_config_hidden(fieldName));
                            widget.setValue(data[fieldName]);

                            form.add(widget);
                        }
                    }
                }
            }

            Ext.resumeLayouts(true);
        }

        function initChangeListForm(adminform) {
            //!TODO: Optimize it!
            var list_display = [],
                fields = [];

            for (var field in adminform.fields) {
                if (!adminform.fields.hasOwnProperty(field))
                    continue;

                list_display.push(field);

                var f = adminform.fields[field];
                f.name = field;
                f.form_model = adminform.model;

                fields.push(f);
            }

            that.add({
                xtype: 'panel',
                border: false,
                title: adminform.verbose_name_plural,
                layout: 'fit',
                items: [
                    Ext.create('Xmin.view.admin.ChangeListPanel', {
                        prefix: adminform.prefix,
                        keyFields: adminform.hidden_fields,
                        xmin_admin: {
                            data: adminform.data
                        },
                        xmin_model: {
                            admin_url: that.token + '?inline=' + adminform.class,
                            columns: adminform.columns,
                            fields: fields,
                            fieldsArr: adminform.fields,
                            list_display: list_display,
                            actions: []
                        },
                        xmin_config: adminform
                    })
                ]
            });
        }

        this.mainForm = this.add({
            xtype: 'panel',
            border: false,
            title: 'Основные данные',
            bodyPadding: 5,
            overflowY: 'scroll'
        });

        this.setActiveTab(0);

        // Формируем основную форму
        initChangeForm(this.adminform);

        // Добавляем инлайн формы
        for (var adminform in this.adminformInline) {
            if (!this.adminformInline.hasOwnProperty(adminform))
                continue;

            adminform = this.adminformInline[adminform];

            initChangeForm(adminform);

            if (!adminform.fieldsets)
                initChangeListForm(adminform);
        }

        this.forms = Ext.ComponentQuery.query('form', this.mainForm);
        this.lists = Ext.ComponentQuery.query('ChangeListPanel', this);
    },


    setValues: function(data) {

        for (var form in this.forms) {
            if (!this.forms.hasOwnProperty(form))
                continue;
            var tt = this.forms[form].getForm().getFields().items;
            values = {};
            for (var i = 0; i < tt.length; i++)
            {
                if (data[tt[i].name] && tt[i].xtype != "relatedfield")
                {
                    try {
                        if (tt[i].xtype == "URLField")
                        {
                            var a = $('#'+tt[i].id+'-link a');
                            a.attr('href', data[tt[i].name]);
                            a.text(data[tt[i].name]);
                            (data[tt[i].name]);
                        }
                        else tt[i].setValue(data[tt[i].name]);

                    }
                    catch (e)
                    {
                        tt[i].value = data[tt[i].name];
                    }

                }
            }
        }
    },

    getValues: function() {
        var values = {};

        for (var form in this.forms) {
            if (!this.forms.hasOwnProperty(form))
                continue;


            values = Ext.merge(values, this.forms[form].getValues());


        }

        for (var list in this.lists) {
            if (!this.lists.hasOwnProperty(list))
                continue;

            values = Ext.merge(values, this.lists[list].getValues());
        }

        return values;
    },

    markInvalid: function(errors) {
        var all_errors = [];

        for (var error in errors) {
            if (!errors.hasOwnProperty(error))
                continue;

            all_errors.push({id: error, msg: errors[error].join('<br/>')});
        }

        for (var form in this.forms) {
            if (!this.forms.hasOwnProperty(form))
                continue;
            try {
                this.forms[form].getForm().isValid();
                this.forms[form].getForm().markInvalid(all_errors);
            }
            catch(err)
            {
                continue;
            }

        }

        for (var list in this.lists) {
            if (!this.lists.hasOwnProperty(list))
                continue;

            this.lists[list].markInvalid(errors);
        }
    },

    commitChanges: function () {
        for (var list in this.lists) {
            if (!this.lists.hasOwnProperty(list))
                continue;

            this.lists[list].commitChanges();
        }
    },

    setWidgetValue: function (widget, data, field, adminform) {
        var w = widget;

        if (widget.xtype == 'fieldcontainer') {
            w = widget.items.items[0];
        }

        if (data && data[field.name]) {
            w.setValue(data[field.name]);
        } else if (field.default) {
            w.setValue(field.default);
        }

        if (data && Ext.Array.contains(['combo', 'relatedfield'], w.xtype)) {
            w.setRawValue(data[field.name + '_display']);
        } else if (data && 'addressfield' == w.xtype) {
            w.setRawValue(data[field.name]);
        }

        if (data && Ext.Array.contains(['FileField'], w.xtype)) {
            w.setRawData(adminform);
        }

        return widget
    }
});
