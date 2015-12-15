from django.conf import settings
from django.db import models


class AuditFieldsMixin(models.Model):
    """
    Базовая модель для учета дат создания/модификации и автора записи/модификации
    """
    class Meta:
        abstract = True

    added_at = models.DateTimeField(verbose_name='Дата и время создания', auto_now_add=True, db_index=True, db_column='addedat')
    modified_at = models.DateTimeField(verbose_name='Дата и время модификации', auto_now=True, db_index=True, db_column='modifiedat')
    added_by_user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Автор', related_name='+', db_column='auth_user_addedby_id')
    modified_by_user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Последние изменения осуществил',
                                         related_name='+', db_column='auth_user_modifiedby_id')