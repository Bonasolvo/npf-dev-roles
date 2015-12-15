Ext.define('Dashboard.view.dashboard.CloseIPSWorkflowButton', {
    extend : 'Ext.Button',
    alias  : 'widget.CloseIPSWorkflowButton',
    text: 'Процесс "Закрытие ИПС"',
    cls: 'workflow_button',
    renderTo: Ext.getBody(),
    listeners: {
        afterrender: function () {
            $('.workflow_button').css("margin-right", '3px');
        }
    },
    handler: function() {
        window.open("#/admin/close_ips/workflow/main/","_self");
    }
});