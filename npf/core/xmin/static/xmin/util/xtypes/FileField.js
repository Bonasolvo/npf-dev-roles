Ext.define('Xmin.util.xtypes.FileField', {
    extend: 'Ext.form.field.File',
    alias  : 'widget.FileField',
    xtype: 'fileuploadfield',
    labelWidth: 50,
    buttonText: 'Выберите файл',
    clearOnSubmit: false,
    submitValue: true,
    value: 'foo',
    fileUpload: true,
    requires  : [
        'Xmin.util.HelpImageAligner'
    ],

    initComponent: function(){
        this.callParent();
    },
    listeners: {
        afterrender: function() {
            function extractInitValues(rawData, name) {
                for (var i in rawData.data) {
                    if (name in rawData.data[i]) {
                        return [rawData.data[i][name], rawData.data[i][name + '_url']]
                    }
                }
            }
            function appendLink() {
                file_name = file_name.replace('./', '');
                var selector = '#' + id + '-inputWrap';
                var html = '<div id="' + id + '-link' + '" style="position: absolute; margin-left: 8px; margin-top: 4px"><a target="_blank" href="' + path + '">' + file_name + '</a></div>';
                $(selector).prepend(html);
            }
            function appendCheckbox() {
                var selector = '#' + id + '-triggerWrap';
                var checkbox_id = 'scan-clear-' + id;
                var html = '<span class="up_file_delete"><input id="ID" type="checkbox" role="file_delete" name="NAME">'.replace('ID', checkbox_id).replace('NAME', name);
                html += '<label for="ID">Очистить</label></span>'.replace('ID', checkbox_id);
                $(selector).append(html);
                $('.up_file_show').css('display', 'table-cell').css('vertical-align', 'top').css('width', '30px').css('padding-left', '3px');
                $('.up_file_delete').css('display', 'table-cell').css('vertical-align', 'top').css('width', '100px').css('padding-left', '2px');
            }

            var id = this.id;
            var name = this.name;
            var initValues = extractInitValues(this.rawData, this.name);
            var file_name = initValues[0];
            var path = initValues[1];
            if (file_name) {
                appendLink();
                appendCheckbox();
            }
            Xmin.util.HelpImageAligner.align(this);
        },
        change: function(fld, value) {
            var newValue = value.replace(/C:\\fakepath\\/g, '');
            fld.setRawValue(newValue);
            var selector = '#' + this.id + '-link';
            $(selector).css('display', 'none');
        }
    },
    setRawData: function(value) {
        this.rawData = value;
    }
});