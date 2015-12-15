# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('counter', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NamedCounter',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(unique=True, max_length=255)),
                ('value', models.PositiveIntegerField(default=1)),
            ],
            options={
                'verbose_name': 'Счетчик',
                'verbose_name_plural': 'Системные счетчики',
                'db_table': 'sys_namedcounter',
            },
        ),
    ]
