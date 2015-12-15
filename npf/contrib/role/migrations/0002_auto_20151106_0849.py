# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('role', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='role',
            name='groups',
            field=models.ManyToManyField(related_name='role_set', help_text='The groups this role belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups', blank=True, related_query_name='role', to='auth.Group'),
        ),
        migrations.AddField(
            model_name='role',
            name='permissions',
            field=models.ManyToManyField(related_name='role_set', help_text='Specific permissions for this role.', verbose_name='role permissions', blank=True, related_query_name='role', to='auth.Permission'),
        ),
    ]
