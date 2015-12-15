from npf.core.workflow.admin.workflow_task import WorkflowTaskInstanceForm, WorkflowTaskInstanceAdmin
from npf.core.workflow.models import WorkflowMyTaskInstance


class WorkflowMyTaskInstanceForm(WorkflowTaskInstanceForm):
    class Meta:
        model = WorkflowMyTaskInstance
        fields = '__all__'


class WorkflowMyTaskInstanceAdmin(WorkflowTaskInstanceAdmin):
    form = WorkflowMyTaskInstanceForm

    def get_queryset(self, request):
        return super(WorkflowMyTaskInstanceAdmin, self)\
            .get_queryset(request).filter(performer=request.user)
