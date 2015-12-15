from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType


class Bookmark(models.Model):
    """
    Модель: Закладка
    """
    content_type = models.ForeignKey(verbose_name='Тип содержимого', to=ContentType, db_column='django_content_type_id')
    user = models.ForeignKey(verbose_name='Пользователь', to=settings.AUTH_USER_MODEL, db_column='auth_user_id')
    record_id = models.BigIntegerField(verbose_name='ИД записи', null=True, blank=True)

    class Meta:
        verbose_name = 'Закладка'
        verbose_name_plural = 'Закладки'
        db_table = 'sys_bookmark'

    def __str__(self):
        model = self.content_type.model_class()
        if not model:
            return super().__str__()
        if self.record_id:
            return '{0}: {1}'.format(model._meta.verbose_name, self.record_id)
        return str(model._meta.verbose_name_plural)