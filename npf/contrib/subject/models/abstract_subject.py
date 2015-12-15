from django.db import models

from npf.core.modelaudit.models import AuditFieldsMixin


class AbstractSubject(AuditFieldsMixin, models.Model):

    class Meta:
        verbose_name = 'Вкладчик/участник'
        verbose_name_plural = 'Вкладчики и участники'
        db_table = 'subjectabstract'

    name = models.CharField(verbose_name='Вкладчик/участник', max_length=255)
    type = models.CharField(verbose_name='Тип', max_length=255, db_index=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.type = self.__class__.__name__
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.name