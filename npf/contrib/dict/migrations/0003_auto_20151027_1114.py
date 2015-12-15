# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dict', '0002_bank_country_legalform_okato_okved_pensionscheme_personstatereason'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentType',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('type_name', models.CharField(max_length=255, blank=True, db_column='typename', null=True, verbose_name='Тип документа')),
            ],
            options={
                'verbose_name': 'Тип документа',
                'verbose_name_plural': 'Типы документов',
                'db_table': 'zlk_documenttype',
            },
        ),
        migrations.RemoveField(
            model_name='bank',
            name='parent',
        ),
        migrations.DeleteModel(
            name='Country',
        ),
        migrations.RemoveField(
            model_name='okato',
            name='parent',
        ),
        migrations.RemoveField(
            model_name='okved',
            name='parent',
        ),
        migrations.DeleteModel(
            name='PensionScheme',
        ),
        migrations.DeleteModel(
            name='PersonStateReason',
        ),
        migrations.AlterField(
            model_name='legalform',
            name='short_name',
            field=models.CharField(max_length=255, db_column='shortname', verbose_name='Краткое наименование'),
        ),
        migrations.AlterModelTable(
            name='legalform',
            table='zlk_legalform',
        ),
        migrations.DeleteModel(
            name='Bank',
        ),
        migrations.DeleteModel(
            name='OKATO',
        ),
        migrations.DeleteModel(
            name='OKVED',
        ),
    ]
