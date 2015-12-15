from django.contrib import admin

from npf.core.workflow.admin.script_command import ScriptCommandAdmin
from npf.core.workflow.admin.workflow_mytask import WorkflowMyTaskInstanceAdmin
from npf.core.workflow.admin.workflow_process import WorkflowProcessAdmin, WorkflowProcessInstanceAdmin
from npf.core.workflow.admin.workflow_task import WorkflowTaskAdmin, WorkflowTaskInstanceAdmin
from npf.core.workflow.admin.workflow_memo import WorkflowMemoAdmin

from npf.core.workflow.models import ScriptCommand, WorkflowProcess, WorkflowProcessInstance, WorkflowTask, \
    WorkflowTaskInstance, WorkflowMyTaskInstance, WorkflowMemo

admin.site.register(ScriptCommand, ScriptCommandAdmin)
admin.site.register(WorkflowProcess, WorkflowProcessAdmin)
admin.site.register(WorkflowProcessInstance, WorkflowProcessInstanceAdmin)
admin.site.register(WorkflowTask, WorkflowTaskAdmin)
admin.site.register(WorkflowTaskInstance, WorkflowTaskInstanceAdmin)
admin.site.register(WorkflowMyTaskInstance, WorkflowMyTaskInstanceAdmin)
admin.site.register(WorkflowMemo, WorkflowMemoAdmin)
