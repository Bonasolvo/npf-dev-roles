Ext.define('Dashboard.view.dashboard.AppointmentWorkflowButton', {
    extend : 'Ext.Button',
    alias  : 'widget.AppointmentWorkflowButton',
    text: 'Процесс "Назначение"',
    cls: 'workflow_button',
    renderTo: Ext.getBody(),
    listeners: {
        afterrender: function () {
            $('.workflow_button').css("margin-right", '3px');
        }
    },
    handler: function() {
        window.open("#/admin/appointment/workflow/main/","_self");
    }
});