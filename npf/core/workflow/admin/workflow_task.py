import datetime

from django import forms
from django.contrib.auth.models import Group
from django.db.models import Q
from django.core import management
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import CommandError
from django.core.urlresolvers import reverse

from npf.core.workflow.models import WorkflowTaskInstance, WorkflowTask
from npf.core.workflow.utils import get_task_performer
from npf.core.xmin.admin import XminAdmin


class WorkflowTaskForm(forms.ModelForm):
    class Meta:
        model = WorkflowTask
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance', None)
        urlname, arguments = self.get_url_params(instance)
        url = reverse(urlname, args=arguments)
        # виджет в дальнейшем используется для передачи дополнительной информации в extjs
        self.fields['user_group'].widget.attrs.update({
            'suggest_url': url  # ссылка для динамической загрузки объектов (групп пользователей)
        })

    def get_url_params(self, instance=None):
        info = (self._meta.model._meta.app_label, self._meta.model._meta.model_name)
        if instance:
            return "admin:%s_%s_change" % info, [instance.pk]
        else:
            return "admin:%s_%s_add" % info, []


class WorkflowTaskAdmin(XminAdmin):

    form = WorkflowTaskForm
    fields = ['name', 'order', 'process', 'content_type', 'action_type', 'user_group', 'due_time',
              'automatic_assignment', 'affects_to_system_date', 'after_close_command']
    list_display = ['name', 'order', 'process', 'content_type', 'action_type', 'user_group',
                    'due_time', 'automatic_assignment', 'affects_to_system_date',
                    'after_close_command', 'version']

    def save_model(self, request, obj, form, change):
        if not change:
            obj.version = 1
            obj.save()
        elif form.has_changed():
            old_versions = self.update_obj_version(obj)
            old_versions.update(last_version=obj)

    def update_obj_version(self, obj):
        old_versions = WorkflowTask.objects.filter(Q(last_version=obj) | Q(pk=obj.pk))
        obj.version += 1
        obj.pk = None
        obj.save()
        return old_versions

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.last_version:
            return WorkflowTask._meta.get_all_field_names()
        return []

    def suggest_items(self, model, suggest_context=None, object_id=None):
        """
        Обработка запроса для динамической подгрузки групп пользователей
        """
        if suggest_context == 'user_group':
            return Group.objects.filter(user__isnull=False)


class WorkflowTaskInstanceForm(forms.ModelForm):
    object_url = forms.URLField(label='Ссылка на объект', required=False)

    required_fields = ['task', 'process', 'performer', 'due_date', 'opened_at']

    class Meta:
        model = WorkflowTaskInstance
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        instance = kwargs.get('instance', None)

        for field in self.required_fields:
            try:
                self.fields[field].required = True
            except KeyError:
                pass
        if instance:
            info = (self._meta.model._meta.app_label, self._meta.model._meta.model_name)
            # виджет в дальнейшем используется для передачи дополнительной информации в extjs
            self.fields['performer'].widget.attrs.update({
                # ссылка для динамической загрузки списка исполнителей
                'suggest_url': '{0}'.format(reverse('admin:%s_%s_change' % info, args=[instance.pk]))
            })
            self.fields['object_url'].initial = self.get_url(instance)

    def get_url(self, instance):
        """
        Получение ссылки на добавление или редактирование объекта в зависомости от типа действия,
        указанного в задаче.
        """
        ct = instance.content_type
        url_pattern, arguments = self.get_url_params(instance)
        url_name = url_pattern.format(ct.app_label, ct.model)
        url = reverse(url_name, args=arguments)
        protocol = self.get_protocol()
        return '{0}://{1}/#{2}'.format(protocol, self.host, url)

    def get_url_params(self, instance):
        if instance.task.action_type == WorkflowTask.ActionType.INSERT:
            return "admin:{0}_{1}_add", []
        else:
            return "admin:{0}_{1}_change", [instance.object_id]

    def get_protocol(self):
        return 'https' if self.is_secure else 'http'

    def save(self, commit=True):
        instance = super().save(commit)
        instance.content_type = instance.task.content_type

        if instance.state == WorkflowTaskInstance.State.OPEN and instance.closed_at:
            """
            В случае, если задача имеет статус "OPEN" и укзано время закрытия, то
            меняем статус на "CLOSED" и создаем следующую по порядку задачу.
            """
            instance.state = WorkflowTaskInstance.State.CLOSED
            try:
                templates = WorkflowTask.objects.filter(order__gt=instance.task.order, last_version__isnull=True)
                task_template = templates.order_by('order')[0:1].get()
                now = datetime.datetime.now()

                if task_template.content_type == instance.content_type:
                    object_id = instance.object_id
                else:
                    object_id = None

                task = WorkflowTaskInstance(
                    task=task_template,
                    process=instance.process,
                    performer=get_task_performer(task_template, instance.process),
                    due_date=now + datetime.timedelta(
                        hours=task_template.due_time.hour,
                        minutes=task_template.due_time.minute,
                        seconds=task_template.due_time.second),
                    opened_at=now,
                    content_type=task_template.content_type,
                    object_id=object_id)
                task.save()
            except ObjectDoesNotExist:
                pass

            if instance.task.after_close_command:
                try:
                    management.call_command(instance.task.after_close_command.command,
                                            interactive=False)
                except CommandError:
                    pass
            instance.save()

        return instance

    def clean(self):
        cleaned_data = super(WorkflowTaskInstanceForm, self).clean()
        if self.instance.is_reassigned():
            self.validate_required_field(cleaned_data, 'object_id')
        return cleaned_data

    def validate_required_field(self, cleaned_data, field_name, message="Обязательное поле"):
        if field_name in cleaned_data and cleaned_data[field_name] is None:
            self._errors[field_name] = self.error_class([message])
            del cleaned_data[field_name]


class WorkflowTaskInstanceAdmin(XminAdmin):
    form = WorkflowTaskInstanceForm

    list_display = ['task', 'process', 'performer', 'opened_at', 'due_date', 'closed_at']
    columns = [{
        'dataIndex': 'task',
        'flex': 1
    }, {
        'dataIndex': 'process',
        'flex': 1
    }, {
        'dataIndex': 'performer',
        'flex': 1
    }, {
        'dataIndex': 'due_date',
        'flex': 1
    }, {
        'dataIndex': 'opened_at',
        'flex': 1
    }, {
        'dataIndex': 'closed_at',
        'flex': 1
    }]

    def suggest_items(self, model, suggest_context=None, object_id=None):
        """
        Обработка запроса для динамической подкрузки исполнителей
        """
        instance = WorkflowTaskInstance.objects.get(pk=object_id)
        if suggest_context == 'performer':
            return instance.task.user_group.user_set.all()

    def get_fields(self, request, obj=None):
        fields = ['task', 'process', 'performer', 'due_date', 'opened_at', 'closed_at']
        has_permission = self.has_add_permission(request) or self.has_change_permission(request)
        if request.user.is_superuser or has_permission:
            fields.append('object_id')
        fields.append('object_url')
        return fields

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = []
        has_permission = self.has_add_permission(request) or self.has_change_permission(request)
        if not (request.user.is_superuser or has_permission):
            readonly_fields = ['task', 'process', 'performer', 'due_date', 'opened_at', 'object_id']
        elif has_permission and not obj is None and not obj.is_reassigned():
            readonly_fields = ['task', 'process', 'due_date', 'opened_at', 'object_id']

        return readonly_fields

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.host = request.get_host()
        form.is_secure = request.is_secure()
        return form
