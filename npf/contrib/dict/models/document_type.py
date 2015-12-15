from django.db import models


class DocumentType(models.Model):

    type_name = models.CharField(verbose_name='Тип документа', max_length=255, blank=True, null=True, db_column='typename')

    class Meta:
        verbose_name = 'Тип документа'
        verbose_name_plural = 'Типы документов'
        db_table = 'zlk_documenttype'

    def __str__(self):
        return self.type_name
