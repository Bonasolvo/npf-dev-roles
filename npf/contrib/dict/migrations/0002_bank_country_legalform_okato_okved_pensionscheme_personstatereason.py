# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dict', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bank',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('name', models.TextField(verbose_name='Банк')),
                ('bik', models.CharField(max_length=9, verbose_name='БИК')),
                ('parent', mptt.fields.TreeForeignKey(to='dict.Bank', null=True, blank=True)),
            ],
            options={
                'verbose_name_plural': 'Банки',
                'verbose_name': 'Банк',
                'db_table': 'dict_bank',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=70, verbose_name='Наименование')),
                ('short_name', models.CharField(max_length=70, verbose_name='Краткое наименование')),
            ],
            options={
                'verbose_name_plural': 'Страны',
                'verbose_name': 'Страна',
                'ordering': ['short_name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LegalForm',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Наименование')),
                ('short_name', models.CharField(max_length=255, verbose_name='Краткое наименование')),
            ],
            options={
                'verbose_name_plural': 'Организационно-правовые формы',
                'verbose_name': 'Организационно-правовая форма',
                'db_table': 'dict_legal_form',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OKATO',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('code', models.CharField(max_length=11, verbose_name='Код', unique=True)),
                ('name', models.CharField(max_length=255, verbose_name='Наименование')),
                ('additional_info', models.CharField(max_length=128, verbose_name='Дополнительная информация', null=True, blank=True)),
                ('parent', mptt.fields.TreeForeignKey(to='dict.OKATO', null=True, blank=True)),
            ],
            options={
                'verbose_name_plural': 'ОКАТО',
                'verbose_name': 'ОКАТО',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OKVED',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('code', models.CharField(max_length=9, verbose_name='Код')),
                ('name', models.TextField(verbose_name='Наименование')),
                ('parent', mptt.fields.TreeForeignKey(to='dict.OKVED', null=True, blank=True)),
            ],
            options={
                'verbose_name_plural': 'ОКВЭД',
                'verbose_name': 'ОКВЭД',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PensionScheme',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Номер')),
            ],
            options={
                'verbose_name_plural': 'Пенсионные схемы',
                'verbose_name': 'Пенсионная схема',
                'db_table': 'dict_pension_scheme',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PersonStateReason',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Наименование')),
            ],
            options={
                'verbose_name_plural': 'Основания статуса Вкладчика/участника',
                'verbose_name': 'Статус Вкладчика/участника (Основание)',
                'db_table': 'dict_person_state_reason',
            },
            bases=(models.Model,),
        ),
    ]
