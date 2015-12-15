Ext.define('Xmin.util.xtypes.ChoicesField', {
   extend: 'Ext.form.field.ComboBox',
   alias: 'widget.choices',

   queryMode: 'local',
   displayField: 'description',
   valueField: 'id',
   editable: false,
   forceSelection: true,
   choices: [],

   initComponent: function () {

       Ext.apply(this, {
          store: Ext.create('Ext.data.Store', {
              fields: ['id', 'description'],
              data: this.choices
          })
       });

       this.callParent(arguments);
   }
});
