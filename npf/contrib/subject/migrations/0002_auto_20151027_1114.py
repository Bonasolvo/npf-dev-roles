# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0002_auto_20151027_1114'),
        ('dict', '0003_auto_20151027_1114'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('subject', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AbstractSubject',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('added_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата и время создания', db_column='addedat')),
                ('modified_at', models.DateTimeField(db_index=True, verbose_name='Дата и время модификации', auto_now=True, db_column='modifiedat')),
                ('name', models.CharField(max_length=255, verbose_name='Вкладчик/участник')),
                ('type', models.CharField(max_length=255, db_index=True, verbose_name='Тип')),
            ],
            options={
                'verbose_name': 'Вкладчик/участник',
                'verbose_name_plural': 'Вкладчики и участники',
                'db_table': 'subjectabstract',
            },
        ),
        migrations.CreateModel(
            name='PensionFund',
            fields=[
                ('abstractsubject_ptr', models.OneToOneField(parent_link=True, to='subject.AbstractSubject', serialize=False, primary_key=True, auto_created=True)),
                ('management_company', models.BooleanField(db_column='managementcompany', default=False, verbose_name='Наличие управляющей компании')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Примечания')),
                ('license', models.CharField(blank=True, max_length=255, null=True, verbose_name='Номер лицензии')),
                ('license_issue_date', models.DateField(blank=True, db_column='licenseissuedate', null=True, verbose_name='Дата выдачи лицензии')),
                ('ovd', models.CharField(blank=True, max_length=255, null=True, verbose_name='ОВД')),
                ('inn', models.CharField(blank=True, max_length=20, null=True, verbose_name='ИНН')),
                ('okpo', models.CharField(blank=True, max_length=20, null=True, verbose_name='ОКПО')),
                ('registration', models.TextField(blank=True, null=True, verbose_name='Зарегистрирован (где и кем)')),
                ('phone', models.CharField(blank=True, max_length=255, null=True, verbose_name='Телефоны')),
                ('fax', models.CharField(blank=True, max_length=155, null=True, verbose_name='Факс')),
                ('region', models.CharField(blank=True, max_length=255, null=True, verbose_name='Действует в регионе')),
                ('additional_information', models.TextField(blank=True, db_column='additionalinformation', null=True, verbose_name='Доп. информация')),
                ('contacts', models.TextField(blank=True, null=True, verbose_name='Контактные данные ключевых сотрудников')),
                ('actual_address', models.OneToOneField(related_name='+', verbose_name='Фактический адрес', to='address.House', db_column='house_actualaddress_id')),
                ('legal_address', models.OneToOneField(related_name='+', verbose_name='Юридический ардес', to='address.House', db_column='house_legaladdress_id')),
                ('legal_form', models.ForeignKey(verbose_name='ОПФ', blank=True, to='dict.LegalForm', db_column='legalform_id', null=True)),
                ('postal_address', models.OneToOneField(related_name='+', verbose_name='Почтовый адрес', to='address.House', db_column='house_postaladdress_id')),
            ],
            options={
                'verbose_name': 'Пенсионный фонд',
                'verbose_name_plural': 'Пенсионный фонд России и другие НПФ',
                'db_table': 'subjectpensionfund',
            },
            bases=('subject.abstractsubject',),
        ),
        migrations.AddField(
            model_name='abstractsubject',
            name='added_by_user',
            field=models.ForeignKey(related_name='+', verbose_name='Автор', to=settings.AUTH_USER_MODEL, db_column='auth_user_addedby_id'),
        ),
        migrations.AddField(
            model_name='abstractsubject',
            name='modified_by_user',
            field=models.ForeignKey(related_name='+', verbose_name='Последние изменения осуществил', to=settings.AUTH_USER_MODEL, db_column='auth_user_modifiedby_id'),
        ),
    ]
