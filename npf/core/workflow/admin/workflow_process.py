import datetime

from django.core.exceptions import ObjectDoesNotExist

from npf.core.workflow.models import WorkflowTaskInstance, WorkflowTask, WorkflowProcess
from npf.core.workflow.utils import get_task_performer
from npf.core.xmin.admin import XminAdmin


class WorkflowProcessAdmin(XminAdmin):
    list_display = ['name', 'document_type', 'active']
    columns = [{
        'dataIndex': 'name',
        'flex': 1
    }, {
        'dataIndex': 'document_type',
        'flex': 1
    }, {
        'dataIndex': 'active',
        'flex': 1
    }]

    def suggest_items(self, model):
        return model.objects.filter(active=True)


class WorkflowProcessInstanceAdmin(XminAdmin):
    list_display = ['process', 'assignment_responsible', 'description']
    columns = [{
        'dataIndex': 'process',
        'flex': 1
    }, {
        'dataIndex': 'assignment_responsible',
        'flex': 1
    }, {
        'dataIndex': 'description',
        'flex': 1
    }]

    def save_model(self, request, obj, form, change):
        pk = obj.pk
        super().save_model(request, obj, form, change)
        if not pk:
            """
            Создание и назначение первой задачи при запуске рабочего процесса
            """
            try:
                templates = WorkflowTask.objects.filter(process=obj.process, last_version__isnull=True)
                task_template = templates.order_by('order')[0:1].get()
                now = datetime.datetime.now()
                task = WorkflowTaskInstance(
                    task=task_template,
                    process=obj,
                    performer=get_task_performer(task_template, obj),
                    due_date=now + datetime.timedelta(
                        hours=task_template.due_time.hour,
                        minutes=task_template.due_time.minute,
                        seconds=task_template.due_time.second),
                    opened_at=now,
                    content_type=task_template.content_type)
                task.save()
            except ObjectDoesNotExist:
                pass

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "process":
            """
            Фильтрация активных рабочих процессов для поля 'process'
            """
            kwargs["queryset"] = WorkflowProcess.objects.filter(active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
