from django.db import models
from django.contrib.contenttypes.models import ContentType


class Template(models.Model):
    """
    Модель: Шаблон печатной формы
    """
    class Meta:
        verbose_name = 'Шаблон'
        verbose_name_plural = 'Шаблоны печатных форм'
        db_table = 'sys_printformtemplate'

    name = models.CharField(verbose_name='Название', max_length=150)
    file_name = models.CharField(verbose_name='Название генерируемого файла', max_length=250, db_column='filename')
    file = models.FileField(verbose_name="Шаблон")
    model = models.ForeignKey(ContentType, null=True, verbose_name="Модель", db_column='django_content_type_id')
    instructions = models.CharField(verbose_name='Инструкции к шаблону', max_length=450)

    def __str__(self):
        return self.name
