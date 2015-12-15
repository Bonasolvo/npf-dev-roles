Ext.define('Xmin.view.dashboard.MyTasks', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.MyTasks',
    overCls: 'x-item-over',
    listeners: {
        beforerender: function () {

            /*
            Ext.Ajax.request({
                url: 'workflow/get_user_tasks',
                method: "GET",
                success: function(response) {
                    var data = Ext.JSON.decode(response.responseText);
                    data = data.result;
                    if (data.length) {
                        var tpl = new Ext.XTemplate(
                            '<ul class="x-my-tasks">',
                            '<tpl for=".">',
                            '<li class="task {priority_en}">',
                            '<a href="{link}"><span class="object_name">{name}</span></a>',
                            '<br>',
                            '<span>приоритет <b>{priority}</b></span>',
                            '<br>',
                            '<span>{created}</span>',
                            '</li>',
                            '</tpl>',
                            '</ul>'
                        );
                    }
                    else {
                        var tpl = new Ext.XTemplate(
                            '<p class="x-my-tasks-no"><b>Нет активных задач</b></p>'
                        );
                    }
                    tpl.overwrite('x-my-tasks-innerCt', data);
                    $('.x-my-tasks .task').hover(
                        function () {
                            $(this).addClass('x-item-over')
                        },
                        function () {
                            $(this).removeClass('x-item-over')
                        }
                    )
                }
            });*/

        }
    }
});