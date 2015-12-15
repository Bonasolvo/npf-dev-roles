Ext.define('Xmin.util.CompileId', {
    singleton: true,
    replace_slashes : function(url) {
        if (url.indexOf('?') > -1) {
            url = url.slice(0, url.indexOf('?'))
        }
        url = url.split('/').join('__');
        return url;
    },
    revert_slashes : function(url) {
        url = url.split('__').join('/');
        return url;
    }
});
