# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import fias.fields.address


class Migration(migrations.Migration):

    dependencies = [
        ('fias', '0001_initial'),
        ('address', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='House',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('street', models.CharField(editable=False, blank=True, max_length=255, db_index=True, verbose_name='Улица')),
                ('index', models.PositiveIntegerField(blank=True, null=True, verbose_name='Почтовый индекс')),
                ('house', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Дом')),
                ('corps', models.CharField(blank=True, max_length=2, null=True, verbose_name='Корпус')),
                ('apartment', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Квартира')),
            ],
            options={
                'db_table': 'zlk_house',
            },
        ),
        migrations.CreateModel(
            name='Street',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('street', models.CharField(editable=False, blank=True, max_length=255, db_index=True, verbose_name='Улица')),
            ],
            options={
                'db_table': 'zlk_street',
            },
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('fias.addrobj',),
        ),
        migrations.CreateModel(
            name='Socr',
            fields=[
            ],
            options={
                'verbose_name': 'Сокращениие наименования адресного объекта',
                'verbose_name_plural': 'Список сокращений',
                'proxy': True,
            },
            bases=('fias.socrbase',),
        ),
        migrations.AddField(
            model_name='street',
            name='fias_street',
            field=fias.fields.address.AddressField(related_name='+', verbose_name='Улица', blank=True, to='fias.AddrObj', null=True),
        ),
        migrations.AddField(
            model_name='house',
            name='fias_house',
            field=fias.fields.address.AddressField(related_name='+', verbose_name='Дом', blank=True, to='fias.AddrObj', db_column='fiashouse', null=True),
        ),
        migrations.AddField(
            model_name='house',
            name='fias_street',
            field=fias.fields.address.AddressField(related_name='+', verbose_name='Улица', blank=True, to='fias.AddrObj', null=True),
        ),
    ]
