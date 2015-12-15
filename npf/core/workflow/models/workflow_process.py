from django.db import models

from npf.contrib.dict.models import DocumentType


class WorkflowProcess(models.Model):
    """
    Модель: Рабочий процесс.
    """
    name = models.CharField(verbose_name='Название', max_length=255, blank=True, null=True)
    document_type = models.ForeignKey(DocumentType, verbose_name='Тип документа',
                                      null=True, blank=True, db_column='documenttype_id')
    active = models.BooleanField(verbose_name='Активен', default=True)

    class Meta:
        verbose_name = 'Рабочий процесс'
        verbose_name_plural = 'Справочник рабочих процессов'
        db_table = 'sys_workflowprocess'

    def __str__(self):
        return '{} ({})'.format(self.name, self.document_type)


class WorkflowProcessInstance(models.Model):
    """
    Модель: Экземпляр рабочего процесса (запущенный рабочий процесс).
    """
    process = models.ForeignKey(WorkflowProcess, verbose_name='Рабочий процесс',
                                null=True, blank=True, db_column='workflowprocess_id')
    assignment_responsible = models.ForeignKey('userprofile.UserProfile', verbose_name='Ответственный за назначения',
                                               db_column='auth_user_assignmentresponsible_id')
    description = models.TextField(verbose_name='Описание', null=True, blank=True)

    class Meta:
        verbose_name = 'Рабочий процесс'
        verbose_name_plural = 'Запущенные рабочие процессы'
        db_table = 'sys_workflowprocessinstance'

    def __str__(self):
        return '{} ({})'.format(self.process, self.description)
