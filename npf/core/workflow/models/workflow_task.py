from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group
from django.db import models
from django.core.urlresolvers import reverse
from .script_command import ScriptCommand
from .workflow_process import WorkflowProcess, WorkflowProcessInstance
from django.contrib.sites.models import Site

class WorkflowTask(models.Model):
    """
    Модель: Шаблон задачи для рабочего процесса.
    """
    class ActionType:
        INSERT = 'i'
        UPDATE = 'u'
        DELETE = 'd'
        CONTROL = 'c'
        CHOICES = (
            (INSERT, 'Ввод данных'),
            (UPDATE, 'Редактирование'),
            (DELETE, 'Удаление'),
            (CONTROL, 'Контроль')
        )

    name = models.CharField(verbose_name='Название задачи', max_length=255, blank=True, null=True)
    order = models.IntegerField(verbose_name='Последовательный номер')
    process = models.ForeignKey(WorkflowProcess, verbose_name='Рабочий процесс', db_column='workflowprocess_id')
    content_type = models.ForeignKey(ContentType, verbose_name='Тип объекта', db_column='django_content_type_id')
    action_type = models.CharField(verbose_name='Тип действия', max_length=1, choices=ActionType.CHOICES,
                                   db_column='actiontype')
    user_group = models.ForeignKey(Group, verbose_name='Группа пользователей', db_column='auth_group_id')
    due_time = models.TimeField(verbose_name='Время на выполнение', blank=True, null=True, db_column='duetime')
    automatic_assignment = models.BooleanField(verbose_name='Автоматическое назначение', default=False,
                                               db_column='automaticassignment')
    affects_to_system_date = models.BooleanField(verbose_name='Влияет на дату системы', default=False,
                                                 db_column='affectstosystemdate')
    after_close_command = models.ForeignKey(ScriptCommand, verbose_name='Комманда после завершении', null=True,
                                            blank=True, db_column='scriptcommand_id')
    version = models.IntegerField(verbose_name='Версия')
    last_version = models.ForeignKey(to='WorkflowTask', verbose_name='Последняя версия', null=True, blank=True,
                                     db_column='workflowtask_lastversion_id')

    class Meta:
        verbose_name = 'Шаблон задачи'
        verbose_name_plural = 'Справочник задач'
        unique_together = ('id', 'order', 'version')
        db_table = 'sys_workflowtask'

    def __str__(self):
        return self.name


class WorkflowTaskInstance(models.Model):
    """
    Модель: Экземпляр задачи.
    """
    class State:
        OPEN = 'o'
        CLOSED = 'c'
        CHOICES = (
            (OPEN, 'Открыта'),
            (CLOSED, 'Закрыта'),
        )

    custom_fields = ['object_url']

    def object_url(self):
        """
        Автогенерируемое поле: ссылка на объект в задаче.
        """
        return "http://" + Site.objects.get_current().domain + "/#" + reverse("admin:%s_%s_change" % (self.content_type.app_label, self.content_type.model),
                               args=(self.object_id,))

    def is_reassigned(self):
        """
        Проверка, была ли задача переназначена ответственным лицом. Используется в случае ручного назначения задачи.
        """
        return self.performer is not None and self.performer.groups.filter(pk=self.task.user_group.pk).exists()

    task = models.ForeignKey(WorkflowTask, verbose_name='Шаблон задачи', db_column='workflowtask_id')
    process = models.ForeignKey(WorkflowProcessInstance, verbose_name='Экземпляр рабочего процесса',
                                db_column='workflowprocessinstance_id')
    performer = models.ForeignKey('userprofile.UserProfile', verbose_name='Исполнитель', null=True, blank=True,
                                  db_column='auth_user_performer_id')
    state = models.CharField(verbose_name='Статус', max_length=1, choices=State.CHOICES, default=State.OPEN)
    due_date = models.DateTimeField(verbose_name='Срок исполнения', blank=True, null=True, db_column='duedate')
    opened_at = models.DateTimeField(verbose_name='Дата и время создания', blank=True, null=True, db_column='openedat')
    closed_at = models.DateTimeField(verbose_name='Дата и время завершения', blank=True, null=True, db_column='closedat')
    object_id = models.PositiveIntegerField(verbose_name='ID объекта', null=True, blank=True, db_column='objectid')
    content_type = models.ForeignKey(ContentType, null=True, blank=True, db_column='django_content_type_id')
    content_object = GenericForeignKey()

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Все задачи'
        db_table = 'sys_workflowtaskinstance'

    def __str__(self):
        return self.task.name
