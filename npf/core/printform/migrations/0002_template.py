# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('printform', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='Название')),
                ('file_name', models.CharField(max_length=250, db_column='filename', verbose_name='Название генерируемого файла')),
                ('file', models.FileField(upload_to='', verbose_name='Шаблон')),
                ('instructions', models.CharField(max_length=450, verbose_name='Инструкции к шаблону')),
                ('model', models.ForeignKey(verbose_name='Модель', to='contenttypes.ContentType', db_column='django_content_type_id', null=True)),
            ],
            options={
                'verbose_name': 'Шаблон',
                'verbose_name_plural': 'Шаблоны печатных форм',
                'db_table': 'sys_printformtemplate',
            },
        ),
    ]
