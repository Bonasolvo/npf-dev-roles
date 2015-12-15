Ext.define('Xmin.util.xtypes.DateTimeField', {
    extend:'Ext.form.FieldContainer',
    mixins: { field: 'Ext.form.field.Field' },
    requires: ['Ext.form.field.Base', 'Xmin.util.HelpImageAligner'],
    alias  : 'widget.DateTimeField',

    layout : 'hbox',

    initComponent: function(){
        this.callParent(arguments);

        var name = this.initialConfig.name;

        // Состоит из двух полей: datefield и timefield
        this.add(
            {
                xtype: 'datefield',
                name: name + '_0',
                flex: 1
            },
            {
                xtype: 'timefield',
                name: name + '_1',
                flex: 1,
            }
        );

        this.datefield = this.query('datefield')[0];
        this.timefield = this.query('timefield')[0];
    },

    listeners: {
        afterrender: function () {
            Xmin.util.HelpImageAligner.align(this);
        }
    },

    setValue: function(value) {
        var timezoneOffset = (new Date()).getTimezoneOffset() * 60000;
        parsed = Date.parse(value);
        datetime = new Date(parsed + timezoneOffset)

        if (!isNaN(datetime)) {
            this.datefield.setValue(datetime);
            this.timefield.setValue(datetime);
        } else {
            this.timefield.setValue(value);
        }

        return this;
    },

    getValue: function() {
        var date = this.datefield.getSubmitValue(),
            time = this.timefield.getSubmitValue();

        if (date && time)
            return Ext.String.format('{0} {1}', date, time);

        return date ? date : time;
    },

    markInvalid: function(errors) {
        this.datefield.markInvalid(errors);
        this.timefield.markInvalid(errors);
    },

    clearInvalid: function(){
        this.datefield.clearInvalid();
        this.timefield.clearInvalid();
    },

    /*
     * Don't return any data for submit; the form will get the info from the individual checkboxes themselves.
     */
    getSubmitData: function() {
        return null;
    },

    /*
     * Don't return any data for the model; the form will get the info from the individual checkboxes themselves.
     */
    getModelData: function() {
        return null;
    }
});
