Ext.define('Xmin.util.HelpImageAligner', {
    singleton: true,
    align : function(that) {
        var owner_id = that.ownerCt.id;
            if (owner_id.indexOf('fieldcontainer') > -1) {
                $('#' + that.id).css('width', '100%').css('margin-bottom', '0px');
            }
    }
});
