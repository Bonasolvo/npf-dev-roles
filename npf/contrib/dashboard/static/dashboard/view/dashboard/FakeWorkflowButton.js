Ext.define('Dashboard.view.dashboard.FakeWorkflowButton', {
    extend : 'Ext.Button',
    alias  : 'widget.FakeWorkflowButton',
    text: 'Процесс "Fake"',
    cls: 'workflow_button',
    renderTo: Ext.getBody(),
    listeners: {
        afterrender: function () {
            $('.workflow_button').css("margin-right", '3px');
        }
    },
    handler: function() {
        window.open("#/admin/fake/workflow/main/","_self");
    }
});