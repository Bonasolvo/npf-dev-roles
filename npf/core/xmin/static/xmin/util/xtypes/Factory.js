Ext.define('Xmin.util.xtypes.Factory', {
    // Регистрация кастомных типов полей

    singleton: true,

    requires : [
        'Xmin.util.xtypes.CustomType',
        'Xmin.util.xtypes.DateField',
        'Xmin.util.xtypes.DateTimeField',
        'Xmin.util.xtypes.IPAddressField',
        'Xmin.util.xtypes.AddressField',
        'Xmin.util.xtypes.RelatedField',
        'Xmin.util.xtypes.FileField',
        'Xmin.util.xtypes.TextField',
        'Xmin.util.xtypes.TextAreaField',
        'Xmin.util.xtypes.HelpImage',
        'Xmin.util.xtypes.MultipleChoiceField',
        'Xmin.util.xtypes.ChoicesField',
        'Xmin.util.xtypes.URLField'
    ],

    django_app_model_field_to_ext_class_map_forms : {
        'testapp.simpletestmodel.name' : {
            xtype : 'xmincustomfield',
            cls   : 'Xmin.util.xtypes.CustomType'
        }
    },

    get_form_field_config : function(field){
        // * Number fields
        // BigIntegerField
        // DecimalField
        // FloatField
        // IntegerField (done)
        // SmallIntegerField
        // PositiveIntegerField
        // PositiveSmallIntegerField
        //
        // * String fields
        // CharField
        // CommaSeparatedIntegerField
        // TextField
        // TextAreaField
        // EmailField
        // IPAddressField
        // GenericIPAddressField
        // URLField
        //
        // * Select fields
        // BooleanField (done)
        // NullBooleanField
        //
        // * Date/Time
        // DateField
        // DateTimeField
        // TimeField
        //
        // AutoField
        // FileField
        // FilePathField
        // ImageField
        // SlugField
        //
        // * Relationship fields
        // ForeignKey
        // ManyToManyField
        // OneToOneField

        var config  = this.get_form_field_config_standard(field),
            mapping = this.django_app_model_field_to_ext_class_map_forms[field.app + "." + field.model + "." + field.name];

        if(mapping) {
            Ext.require(mapping.cls);
            config.xtype = mapping.xtype;
        }
        else {
            // field.widget - виджет из django
            // Сопоставляем поля из django с полями extjs (кастомными или стандартными)
            switch (field.widget) {
                case 'django.contrib.auth.forms.ReadOnlyPasswordHashWidget':
                    Ext.apply(config, {xtype: 'TextField', disabled: true});
                    break;
                case 'django.contrib.admin.widgets.AdminIntegerFieldWidget':
                    config.xtype = 'numberfield';
                    break;
                case 'django.forms.widgets.CheckboxInput':
                    config.xtype = 'checkboxfield';
                    break;
                case 'django.contrib.admin.widgets.AdminDateWidget':
                    config.xtype = 'datefield';
                    break;
                case 'django.contrib.admin.widgets.AdminSplitDateTime':
                    config.xtype = 'DateTimeField';
                    break;
                case 'django.contrib.admin.widgets.RelatedFieldWidgetWrapper':
                    if (field.class == 'django.forms.models.ModelMultipleChoiceField') {
                        config.xtype = 'multiplechoicefield';
                    } else if (field.model) {
                        Ext.apply(config, {xtype: 'relatedfield', model: field.model, suggest_url: field.suggest_url});
                    }
                    break;
                case 'django.forms.widgets.Select':
                    if (field.choices) {
                        Ext.apply(config, {xtype: 'choices', choices: field.choices });
                    }
                    break;
                case 'mptt.forms.TreeNodeChoiceField':
                    config = Ext.apply(config, this.get_form_field_config_foreignkey(field));
                    break;
                case 'fias.widgets.AddressSelect2':
                    Ext.apply(config, {xtype: 'addressfield', url: '/fias/suggest_sbs/'});
                    break;
                case 'django.contrib.admin.widgets.AdminFileWidget':
                    config.xtype = 'FileField';
                    break;
                case 'django.forms.widgets.PasswordInput':
                    Ext.apply(config, {xtype: 'TextField', inputType: 'password'});
                    break;
                case 'django.forms.widgets.URLInput':
                    config.xtype = 'URLField';
                    break;
                case 'django.contrib.admin.widgets.AdminTimeWidget':
                    config.xtype = 'timefield';
                    break;
                case 'django.contrib.admin.widgets.AdminTextareaWidget':
                    config.xtype = 'TextAreaField';
                    break;
                default:
                    config.xtype = 'TextField';
                    break;
            }
        }

        config = this.process_help_text_config(config);
        return config;
    },

    get_form_field_config_standard : function(field){
        // FIELD OPTIONS (and default values)
        // max_length=None,
        // default=NOT_PROVIDED,
        // blank=False,
        // verbose_name=None,
        // editable=True,
        // choices=None,

        // error_messages=None
        // help_text='',

        // primary_key=False,
        // serialize=True,
        // rel=None,
        // name=None,
        // auto_created=False,
        // unique=False,
        // unique_for_date=None,
        // unique_for_month=None,
        // unique_for_year=None,
        // null=False,
        // validators=[],

        var config,
            label = Xmin.util.Text.capfirst(field.verbose_name);


        if (field.allow_blank === false) {
            label = '<b>'+label+'</b>';
        }

        config = {
            helpText: field.help_text,
            fieldLabel: label,
            name: field.name,
            disabled: !field.editable,
            allowBlank: field.allow_blank,
            value: field.default,
            maxLength: field.max_length || Number.MAX_VALUE
        };

        return config;
    },

    get_form_field_config_foreignkey : function(field) {
        return {
            xtype: 'relatedfield',
            model: field.model,
            form_model: field.form_model
        }
    },

    get_form_field_config_hidden: function (field_name, field_value) {
        return {
            xtype: 'hidden',
            name: field_name,
            value: field_value
        }
    },

    process_help_text_config: function (config) {
        if (config.helpText && !config.disabled) {
            var new_config = {};
            var image = Ext.create('Xmin.util.xtypes.HelpImage', {help_text: config.helpText});
            new_config.name = config.name;
            new_config.xtype = 'fieldcontainer';
            new_config.layout = {
                type: 'table',
                columns: 2
            };
            new_config.fieldLabel = config.fieldLabel;
            delete config["fieldLabel"];
            new_config.defaults = {
                bodyStyle: 'margin-bottom: 0px'
            };
            new_config.items = [
                config,
                image];
            return new_config;
        }
        return config;
    }
});
