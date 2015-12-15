from django.db import models


class ScriptCommand(models.Model):
    """
    Модель: Команда для запуска из рабочего процесса
    """
    name = models.CharField(verbose_name='Название', max_length=255)
    description = models.TextField(verbose_name='Описание', blank=True, null=True)
    command = models.TextField(verbose_name='Команда для запуска')

    class Meta:
        verbose_name = 'Команда'
        verbose_name_plural = 'Справочник команд'
        db_table = 'sys_scriptcommand'

    def __str__(self):
        return self.name
