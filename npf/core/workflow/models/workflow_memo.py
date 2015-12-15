from django.db import models
from django.core.validators import MaxValueValidator

from npf.contrib.common.validators import FutureOnlyValidator

from .workflow_process import WorkflowProcessInstance


class WorkflowMemo(models.Model):
    """
    Модель: Служебная записка
    """
    class Type:
        BUG = 'b'
        TASK = 't'
        IMPROVEMENT = 'i'
        CHOICES = (
            (BUG, 'Ошибка'),
            (TASK, 'Задача'),
            (IMPROVEMENT, 'Улучшение'),
        )

    class Status:
        OPENED = 'o'
        RESOLVED = 'r'
        CLOSED = 'c'
        CHOICES = (
            (OPENED, 'Открыта'),
            (RESOLVED, 'Выполнена'),
            (CLOSED, 'Закрыта'),
        )

    title = models.CharField('Заголовок', max_length=255)
    created = models.DateTimeField('Дата создания', auto_now_add=True)
    due_date = models.DateTimeField('Срок исполнения', validators=[FutureOnlyValidator()], db_column='duedate')
    deadline = models.DateTimeField('Крайний срок исполнения', validators=[FutureOnlyValidator()],
                                    blank=True, null=True)
    why_critical = models.TextField('Почему данная задача является критической',
                                    blank=True, null=True, db_column='whycritical')
    task_type = models.CharField('Характер задачи', max_length=1, choices=Type.CHOICES, db_column='tasktype')
    status = models.CharField('Статус', max_length=1, choices=Status.CHOICES,
                              default=Status.OPENED)
    text = models.TextField('Текст задачи')
    estimation = models.CharField('Временная оценка', max_length=100, blank=True, null=True)
    employment_rate = models.PositiveIntegerField('Процент занятости исполнителя',
                                                  validators=[MaxValueValidator(100)], db_column='employmentrate')
    relatedmemos = models.ManyToManyField('self', verbose_name='Связанные задачи', blank=True)
    customer = models.ForeignKey('userprofile.UserProfile', editable=False, blank=True, null=True, db_column='auth_user_customer_id')
    current_participant = models.ForeignKey('workflow.Participant', editable=False,
                                            blank=True, null=True, on_delete=models.SET_NULL, db_column='workflowparticipant_id')
    process_instance = models.ForeignKey(WorkflowProcessInstance, verbose_name='Рабочий процесс',
                                         blank=True, null=True, db_column='workflowprocessinstance_id')
    complete = models.BooleanField('Завершить', default=False)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Служебная записка'
        verbose_name_plural = 'Служебные записки'
        db_table = 'sys_workflowmemo'


class Participant(models.Model):
    """
    Модель: Участник процесса выполнения служебной записки
    """
    class Role:
        OPERATOR = 'o'
        PERFORMER = 'p'
        CHOICES = (
            (OPERATOR, 'Оператор'),
            (PERFORMER, 'Исполнитель'),
        )

    memo = models.ForeignKey(WorkflowMemo, verbose_name='Записка', db_column='workflowmemo_id')
    user = models.ForeignKey('userprofile.UserProfile', verbose_name='Сотрудник', db_column='auth_user_id')
    role = models.CharField('Роль', max_length=1, choices=Role.CHOICES)
    spent = models.PositiveIntegerField('Затраченное время', blank=True, null=True)
    incoming_date = models.DateTimeField('Дата поступления', blank=True, null=True, db_column='incomingdate')
    completion_date = models.DateTimeField('Дата завершения', blank=True, null=True, db_column='completiondate')

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    class Meta:
        verbose_name = 'Участник'
        verbose_name_plural = 'Участники'
        db_table = 'sys_workflowparticipant'


class Attachment(models.Model):
    """
    Модель: Приложение к служебной записке (файл)
    """
    memo = models.ForeignKey(WorkflowMemo, verbose_name='Записка', db_column='workflowmemo_id')
    document = models.FileField('Файл', blank=True)

    class Meta:
        verbose_name = 'Прикрепленный файл'
        verbose_name_plural = 'Прикрепленные файлы'
        db_table = 'sys_workflowattachment'
