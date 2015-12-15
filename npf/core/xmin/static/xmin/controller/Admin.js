Ext.define('Xmin.controller.Admin', {
    extend: 'Ext.app.Controller',

    requires: [
        'Xmin.data.Store',
        'Xmin.util.Text',
        'Xmin.util.Messages',
        'Xmin.selection.DeleteRowModel',
        'Xmin.selection.CellModel',
        'Xmin.grid.CellEditor',
        'Xmin.grid.filters.filter.Choices',
        'Xmin.grid.filters.filter.Related',
        'Xmin.grid.filters.filter.Address'
    ],

    views: [
        'admin.RoutableWindow',
        'admin.ChangeListPanel',
        'admin.ChangeListWindow',
        'admin.ItemChangePanel',
        'admin.ItemChangeWindow',
        'admin.ChangePasswordPanel',
        'admin.ChangePasswordPanelDone'
    ],

    stores: [
    ],

    models: [
    ],

    refs: [
    ],

    init: function() {
        this.registerAdminUrls();

        this.control({
            // Обработчики событий для элементов управления в табличных представлениях
            // и на формах редактирования

            'ChangeListPanel button[name="add_button"]':{
                click : this.onChangeListAdd
            },

            'ChangeListPanel button[name="search_button"]':{
                click : this.onChangeListSearch
            },

            'ChangeListPanel textfield[name="search_query"]':{
                specialkey : function(field, e, eOpts){
                    if (e.getKey() == e.ENTER) {
                        this.onChangeListSearch(field, e, eOpts);
                    }
                }
            },

            'ChangeListPanel button[name="actions_menu"] menuitem':{
                click: this.onChangeListSelectAction
            },

            'ChangeListTreePanel button[name="actions_menu"] menuitem':{
                click: this.onChangeListTreeSelectAction
            },

            '#ChangeListGrid':{
                itemdblclick: this.onChangeListItemEdit,
                selectionchange : this.onChangeListSelectionChange
            },

            //'ItemChangePanel urlfield':{
            //    click: this.onChangeListItemEdit
            //},

            '#ChangeListTreeGrid':{
                itemdblclick: this.onChangeListItemEdit
            },

            'ItemAddPanel button[name="save_button"]':{
                click: this.onAddItemSave
            },

            'ItemAddPanel button[name="save_and_edit_button"]':{
                click: this.onAddItemSaveAndContinueEditing
            },

            'ItemChangePanel button[name="delete_button"]':{
                click: this.onChangeItemDelete
            },

            'ItemChangePanel button[name="save_and_edit_button"]':{
                click: this.onChangeItemSaveAndContinueEditing
            },

            'ItemChangePanel button[name="save_button"]':{
                click: this.onChangeItemSave
            }

        });

        this.application.on({
            server_event: this.onServerEvent,
            scope: this
        });
    },

    registerAdminUrls: function() {
        var router = this.getController('Router'),
            urls   = [],
            that   = this;

        urls.push({
            pattern: '^' + Xmin.settings.urls.logout +'$',
            callback: that.logout
        });

        urls.push({
            pattern: '^' + Xmin.settings.urls.password_change +'$',
            callback: that.changePassword
        });

        urls.push({
            pattern: '^' + Xmin.settings.urls.password_change + 'done' +'$',
            callback: that.changePasswordDone
        });

        // Добавление маршрутизации для всех приложений и моделей django,
        // которые передаются при инициализации приложения
        Ext.Array.forEach(Xmin.settings.app_list, function(item, index, allItems){
            urls.push({
                pattern  : '^'+item.app_url+'$',
                callback : that.appIndexFactory(item)
            });

            Ext.Array.forEach(item.models, function(item, index, allItems){
                if (item.admin_url) {
                    urls.push(
                        {
                            // URL для просмотра тебличного представления
                            pattern: '^'+item.admin_url+'$',
                            callback: that.changeListWindowFactory(item)
                        },
                        {
                            // URL для добавления/редактирования записей
                            pattern: '^'+item.admin_url+'(?!add).*',
                            callback: that.itemChangeWindowFactory(item)
                        }
                    );
                }

                if (item.add_url)
                    urls.push(
                        {
                            pattern: '^'+item.add_url+'$',
                            callback: that.itemAddWindowFactory(item)
                        }
                    );
            });
        });

        router.registerUrls(urls);
    },

    routableWindowFactory: function(model_config, class_path, window_config) {
        Ext.require(class_path);

        return function openRoutableWindow(token){
            // Пытаемся получить ранее созданное окно с токеном
            var routable_window = Ext.ComponentQuery.query('window[xmin_token="'+token+'"]')[0];

            if (routable_window){
                // Если удалось получить, то открываем и устанавливаем на него фокус.
                routable_window.show().focus();
            }
            else {
                // Иначе создаем новое окно.
                var window_title = window_config ? window_config.title : gettext('Window');
                var window = Ext.create(class_path, {
                    title : window_title,
                    xmin_token : token,
                    xmin_model : model_config
                });

                window.show();
            }
        }
    },

    appIndexFactory: function(config) {
        return function(token){
        }
    },

    changeListWindowFactory: function(config) {
        var window_config = {
            title : Xmin.util.Text.capfirst(config.verbose_name_plural)
        };

        return this.routableWindowFactory(config, 'Xmin.view.admin.ChangeListWindow', window_config);
    },

    onChangeListSearch : function(widget, event, eOpts) {
        // Добавляем к текущему url поисковый параметр q и перезагружаем данные
        var this_window = widget.up('panel'),
            query_field = this_window.down('textfield[name="search_query"]'),
            grid  = this_window.down('grid'),
            store = grid.getStore(),
            proxy = store.getProxy();

        proxy.extraParams['q'] = query_field.getValue();
        store.reload();
    },

    onChangeListAdd : function(button, event, eOpts) {
        // переход на страницу ./add/ для добавления новой записи
        var this_window    = button.up('panel'),
            model_token    = this_window.xmin_model.admin_url,
            add_item_token = model_token + 'add/',
            router         = this.getController('Router');

        router.navigate(add_item_token);
    },

    onChangeListItemEdit: function(view, record, item, index, e, eOpts) {
        // переход на страницу ./{id}/ для редактирования записи
        var this_window = view.up('panel');

        if (this_window.xtype == 'changeListPanel' && this_window.isInline)
            return;

        var model_token = this_window.xmin_model.admin_url,
            change_item_token = model_token + record.get('id') + '/',
            router = this.getController('Router');

        router.navigate(change_item_token);
    },

    onChangeListSelectionChange: function(selection_model, selected, eOpts) {
        // При изменении выделения в табличном представлении меняем подпись в статусной строке
        var store = selection_model.getStore(),
            count = store.getCount(),
            token = store.xmin_token,
            panel = Ext.ComponentQuery.query('panel[xmin_token="'+token+'"]')[0],
            status_field = panel.down('[name="status_field"]'),
            selected_count = selected.length;

        if (status_field) {
            status_field.setText(interpolate(
                ngettext('Выбрано записей: %(sel)s из %(cnt)s', 'Выбрано записей: %(sel)s из %(cnt)s', selected_count),
                {sel: selected_count, cnt: count}, true));
        }
    },

    onChangeListTreeSelectAction: function(menu_item, e, eOpts, confirm) {
        // Массовые действия над выделенными объектами в древовидном представлении (пр.: массовое удаление)
        var action = menu_item.name,
            grid = menu_item.up('tree-grid'),
            token = grid.xmin_token,
            store = grid.getStore(),
            selection = grid.getSelectionModel().getSelection(),
            selected = Ext.Array.map(selection, function(item) {
                return item.get('id')
            }),
            req_params = { action: action, _selected_action : selected },
            that = this;

        if (confirm === 'YES') {
            req_params.post = 'yes'
        }

        Ext.Ajax.request({
            url: Xmin.settings.urls.xmin_data + token + 'action/',
            method: 'POST',
            params: req_params,
            success: function(response) {
                var app_response = Ext.JSON.decode(response.responseText);
                if (app_response.success) {
                    if (app_response.confirmation) {
                        var confirmation = app_response.confirmation.replace(/a href="\/admin/g, 'a href="#/admin');
                        Ext.Msg.show({
                            title: 'Вы уверены?',
                            msg: confirmation,
                            icon: Ext.Msg.QUESTION,
                            buttons: Ext.Msg.YESNO,
                            fn: function(buttonId, text, opt) {
                                if (buttonId === 'yes') {
                                    that.onChangeListTreeSelectAction(menu_item, e, eOpts, 'YES');
                                }
                            }
                        });
                    }
                    else {
                        var container = grid.ownerCt,
                            xmin_token = grid.xmin_token,
                            xmin_model = grid.xmin_model;
                        grid.destroy();

                        Ext.Ajax.request({
                            url: Xmin.settings.urls.xmin_data + token,
                            method: 'GET',
                            success: function(response) {
                                var app_response = Ext.JSON.decode(response.responseText);
                                container.add(
                                    Ext.create('Xmin.view.admin.ChangeListPanelTree', {
                                        xmin_token: xmin_token,
                                        xmin_model: xmin_model,
                                        xmin_admin: app_response
                                    })
                                );
                            }
                        });
                    }
                }
                else {
                    Xmin.util.Messages.serverError(response);
                }
            }
        });
    },

    onChangeListSelectAction: function(menu_item, e, eOpts, confirm) {
        // Массовые действия над выделенными объектами в табличном представлении (пр.: массовое удаление)
        function createDoc() {
            var ids = [];
            for (i in selection) {
                ids.push(selection[i].id);
            }
            if (ids.length) {
                var data = {
                    'create_doc': true,
                    'ids': JSON.stringify(ids),
                    'doc_name': action.replace('create_doc_', '')
                };
                $("body").append('<iframe src="' + Xmin.settings.urls.xmin_data + token + ids[0] + '?' + $.param(data) + '" style="display: none;" ></iframe>');
            }
        }
        var action = menu_item.name,
            grid = menu_item.up('grid'),
            token = grid.xmin_token,
            store = grid.getStore(),
            selection = grid.getSelectionModel().getSelection(),
            selected = Ext.Array.map(selection, function(item) { return item.get('id') }),
            req_params = { action: action, _selected_action : selected },
            that = this;
        if (action.indexOf('create_doc') > -1) {
            if (action != 'create_doc') {
                createDoc();
            }
        }
        else {
            if (confirm === 'YES') {
                req_params.post = 'yes'
            }
            Ext.Ajax.request({
                url: Xmin.settings.urls.xmin_data + token + 'action/',
                method: 'POST',
                params: req_params,
                success: function(response) {
                    var app_response = Ext.JSON.decode(response.responseText);
                    if (app_response.success) {
                        if (app_response.confirmation) {
                            var confirmation = app_response.confirmation.replace(/a href="\/admin/g, 'a href="#/admin');

                            Ext.Msg.show({
                                title: 'Вы уверены?',
                                msg: confirmation,
                                icon: Ext.Msg.QUESTION,
                                buttons: Ext.Msg.YESNO,
                                fn: function(buttonId, text, opt) {
                                    if (buttonId === 'yes') {
                                        that.onChangeListSelectAction(menu_item, e, eOpts, 'YES');
                                    }
                                }
                            });
                        }
                        else {
                            store.load();
                        }
                    }
                    else {
                        Xmin.util.Messages.serverError(response);
                    }
                }
            });
        }
    },

    itemAddWindowFactory: function(config) {
        var window_config = {
            title : Xmin.util.Text.capfirst(config.verbose_name)
        };
        return this.routableWindowFactory(config, 'Xmin.view.admin.ItemAddWindow', window_config);
    },

    onItemSave: function(button, method, continue_editing) {

        var item_chnage_panel = button.up('panel'),
            token = item_chnage_panel.xmin_token,
            that = this;

        function extractFiles() {
            var file_fields = [];
            var panel_id = item_chnage_panel.id;
            var file_inputs = $('#' + panel_id + ' input[type=file]');

            if (file_inputs.length) {
                for (i = 0; i < file_inputs.length; i++) {
                    if (file_inputs[i].files.length) {
                        file_fields.push({
                            'name': file_inputs[i].name,
                            'file': file_inputs[i].files[0]
                        })
                    }
                }
            }
            return file_fields;
        }

        function sendDataWithXHR() {
            var formData = new FormData();
            for (i = 0; i < files.length; i++) {
                formData.append(files[i].name, files[i].file);
            }
            for (var key in form_values) {
                if (form_values.hasOwnProperty(key)) {
                    formData.append(key, form_values[key]);
                }
            }
            var xhr = new XMLHttpRequest();
            var xhr_url = Xmin.settings.urls.xmin_data + token;
            xhr.open('POST', xhr_url, true);
            xhr.setRequestHeader('X-CSRFToken', Ext.util.Cookies.get('csrftoken'));
            xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
            xhr.onload = function (e) {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        var app_response = Ext.JSON.decode(xhr.responseText);
                        item_chnage_panel.setLoading(false);
                        if (app_response.success) {
                            item_chnage_panel.commitChanges();
                            app_response.event.item_window = item_chnage_panel;
                            app_response.event.continue_editing = continue_editing;
                            that.getController('ServerEvents').recieveEvent(app_response.event);
                            item_chnage_panel.adminform.data = app_response.data;
                            item_chnage_panel.setValues(app_response.data);
                        }
                        else {
                            item_chnage_panel.markInvalid(app_response.errors);
                        }
                    }
                }
            };
            xhr.onerror = function (e) {
                item_chnage_panel.setLoading(false);
            };
            xhr.send(formData);
        }

        function extractDeleteCheckboxes() {
            var checked = [];
            var panel_id = item_chnage_panel.id;
            var delete_checks = $('#' + panel_id + ' input[type=checkbox][role=file_delete]');
            for (i = 0; i < delete_checks.length; i++) {
                if (delete_checks[i].checked) {
                    checked.push(delete_checks[i].name + '-clear');
                }
            }
            return checked;
        }

        function mergeValues(form_values, delete_checkboxes) {
            for (i = 0; i < delete_checkboxes.length; i++) {
                form_values[delete_checkboxes[i]] = 'on';
            }
            return form_values;
        }

        function clearFiles(files, delete_checkboxes) {
            var cleaned = [];
            for (i = 0; i < files.length; i++) {
                if (delete_checkboxes.indexOf(files[i].name + '-clear') == -1) {
                    cleaned.push(files[i]);
                }
            }
            return cleaned;
        }

        function get_raw_fields_from_string(values){
            var fields = values.split('&');
            for(var i = 0, result = {}; i < fields.length; i++){
                fields[i] = fields[i].split('=');
                result[fields[i][0]] = decodeURIComponent(fields[i][1]);
            }
            return result;
        }

        function clean_raw_field(values) {
            if( typeof values === 'string' ) {
                values = get_raw_fields_from_string(values);
            }

            for (var field in values) {
                if (values.hasOwnProperty(field) && field.indexOf('_raw') > -1) {
                    var value = values[field];
                    delete values[field];
                    if (value) {
                        values[field.replace('_raw', '')] = value.split(',');
                    }
                }
            }
            return values;
        }

        item_chnage_panel.setLoading('Сохранение...');

        // Получаем список файлов и записи на удаление в инлайн формах
        var form_values = item_chnage_panel.getValues();
        var files = extractFiles();
        var delete_checkboxes = extractDeleteCheckboxes();

        if (delete_checkboxes) {
            // Дабавляем метку для удаляемых записей и помечаем соответствующие файлы на удаление
            form_values = mergeValues(form_values, delete_checkboxes);
            files = clearFiles(files, delete_checkboxes);
        }

        // Если нужно отправить файлы то делаем запрос через XHR
        if (files.length || delete_checkboxes.length) {
            sendDataWithXHR();
        }
        else {
            // Иначе щлем форму через ajax
            var values = item_chnage_panel.getValues();
            values = clean_raw_field(values);
            Ext.Ajax.request({
                url: Xmin.settings.urls.xmin_data + token,
                method: 'POST',
                params: values,
                success: function(response) {
                    var app_response = Ext.JSON.decode(response.responseText);
                    item_chnage_panel.setLoading(false);
                    if (app_response.success) {
                        item_chnage_panel.commitChanges();
                        app_response.event.item_window = item_chnage_panel;
                        app_response.event.continue_editing = continue_editing;
                        that.getController('ServerEvents').recieveEvent(app_response.event);
                        item_chnage_panel.adminform.data = app_response.data;
                        item_chnage_panel.setValues(app_response.data);
                    }
                    else {
                        item_chnage_panel.markInvalid(app_response.errors);
                    }
                },
                failure: function(error) {
                    item_chnage_panel.setLoading(false);
                }
            });
        }
    },

    onItemDelete: function(button, confirm) {
        var item_window = button.up('panel'),
            form = item_window.down('form').getForm(),
            token = item_window.xmin_token,
            req_params = {},
            that = this;
        if (confirm === 'YES') {
            req_params.post = 'yes'
        }

        // Делаем ajax запрос на удаление, запрашиваем подтверждение у пользователя
        // и делаем повторных запрос с меткой подтверждения
        Ext.Ajax.request({
            url: Xmin.settings.urls.xmin_data + token,
            method: 'DELETE',
            params: req_params,
            success: function(response) {
                var app_response = Ext.JSON.decode(response.responseText);

                if (app_response.success) {
                    if (app_response.confirmation) {
                        var confirmation = app_response.confirmation.replace(/a href="\/admin/g, 'a href="#/admin');

                        Ext.Msg.show({
                            title: 'Вы уверены?',
                            msg: confirmation,
                            icon: Ext.Msg.QUESTION,
                            buttons: Ext.Msg.YESNO,
                            fn: function(buttonId, text, opt) {
                                if (buttonId === 'yes') {
                                    that.onItemDelete(button, 'YES');
                                }
                            }
                        });
                    }
                    else {
                        app_response.event.item_window = item_window;
                        that.getController('ServerEvents').recieveEvent(app_response.event);
                    }
                }
                else {
                    Xmin.util.Messages.serverError(response);
                }

            }
        });
    },

    onAddItemSave: function(button, continue_editing) {
        var method = 'POST';
        this.onItemSave(button, method, continue_editing);
    },

    onAddItemSaveAndContinueEditing: function(button) {
        var continue_editing = true;
        this.onAddItemSave(button, continue_editing);
    },

    itemChangeWindowFactory: function(config) {
        var window_config = {
            title : Xmin.util.Text.capfirst(config.verbose_name)
        };
        return this.routableWindowFactory(config, 'Xmin.view.admin.ItemChangeWindow', window_config);
    },

    onChangeItemSave: function(button, continue_editing) {
        var method = 'PUT';
        this.onItemSave(button, method, continue_editing);
    },

    onChangeItemSaveAndContinueEditing: function(button) {
        var continue_editing = true;
        this.onChangeItemSave(button, continue_editing);
    },

    onChangeItemDelete: function (button) {
        this.onItemDelete(button);
    },

    onServerEvent: function(event){
        if (event.action === 'ADDITION') {
            this.handleServerAddEvent(event);
        }

        if (event.action === 'CHANGE') {
            this.handleServerChangeEvent(event);
        }

        if (event.action === 'DELETION') {
            this.handleServerDeleteEvent(event);
        }
    },

    handleServerAddEvent: function(event) {
        var token = event.token,
            change_list_token    = token.split('/').slice(0,-2).join('/') + '/',
            change_list_store_id = '/store/buffered' + change_list_token,
            simple_list_store_id = '/store/simple' + change_list_token,
            action_list_store_id = '/store/actions' + change_list_token,
            change_list_store    = Ext.data.StoreManager.lookup(change_list_store_id),
            simple_list_store    = Ext.data.StoreManager.lookup(simple_list_store_id);
            action_list_store    = Ext.data.StoreManager.lookup(action_list_store_id);

        // Update the List window store (if loaded)
        if (change_list_store) {
            change_list_store.load();
        }

        // Update the List window store (if loaded)
        if (simple_list_store) {
            simple_list_store.load();
        }

        if (action_list_store) {
            action_list_store.load();
        }

        if(event.item_window) {
            // The event originated in a local window
            var form  = event.item_window.down('form').getForm(),
                router = this.getController('Router');

            form.setValues(event.object);
            event.item_window.ownerCt.close();
            if(event.continue_editing === true) {
                router.navigate(change_list_token + event.object.id + '/');
            }
        }
    },

    handleServerChangeEvent: function(event) {
        var token = event.token,
            change_list_token    = token.split('/').slice(0,-2).join('/') + '/',
            change_list_store_id = '/store/buffered' + change_list_token,
            action_list_store_id = '/store/actions' + change_list_token,
            change_list_store    = Ext.data.StoreManager.lookup(change_list_store_id);
            action_list_store    = Ext.data.StoreManager.lookup(action_list_store_id);

        // Update the List window store (if loaded)
        if (change_list_store) {
            change_list_store.load();
        }

        if (action_list_store) {
            action_list_store.load();
        }

        if(event.item_window) {
            // The event originated in a local window
            var form  = event.item_window.down('form').getForm();

            //TODO fix set form values on change event
            //form.setValues(event.object);

            if(event.continue_editing !== true) {
                event.item_window.ownerCt.close();
            }
        }
    },

    handleServerDeleteEvent: function(event) {
        var token = event.token,
            change_list_token    = token.split('/').slice(0,-2).join('/') + '/',
            action_list_store_id = '/store/actions' + change_list_token,
            change_list_store_id = '/store/buffered' + change_list_token,
            action_list_store    = Ext.data.StoreManager.lookup(action_list_store_id);
            change_list_store    = Ext.data.StoreManager.lookup(change_list_store_id);

        // Update the List window store (if loaded)
        if (change_list_store) {
            change_list_store.load();
        }

        if (action_list_store) {
            action_list_store.load();
        }

        if (event.item_window) {
            event.item_window.ownerCt.close();
        }
    },

    logout: function() {
        Ext.Ajax.request({
            url: Xmin.settings.urls.logout,
            method: 'GET',
            headers: { 'Authorization': null },
            success: function(response) {
                //document.location = '/';
            },
            failure: function(response, options) {
                if (response.status == 401) {
                    document.documentElement.innerHTML = response.responseText;
                    document.location = '/';
                }
            }
        });
    }
});
