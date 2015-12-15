# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bookmark',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('record_id', models.BigIntegerField(blank=True, null=True, verbose_name='ИД записи')),
                ('content_type', models.ForeignKey(verbose_name='Тип содержимого', to='contenttypes.ContentType', db_column='django_content_type_id')),
                ('user', models.ForeignKey(verbose_name='Пользователь', to=settings.AUTH_USER_MODEL, db_column='auth_user_id')),
            ],
            options={
                'verbose_name': 'Закладка',
                'verbose_name_plural': 'Закладки',
                'db_table': 'sys_bookmark',
            },
        ),
    ]
