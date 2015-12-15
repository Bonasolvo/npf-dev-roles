# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import django.core.validators
import npf.contrib.common.validators.future_only
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dict', '0003_auto_20151027_1114'),
        ('auth', '0006_require_contenttypes_0002'),
        ('workflow', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('document', models.FileField(blank=True, upload_to='', verbose_name='Файл')),
            ],
            options={
                'verbose_name': 'Прикрепленный файл',
                'verbose_name_plural': 'Прикрепленные файлы',
                'db_table': 'sys_workflowattachment',
            },
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('role', models.CharField(choices=[('o', 'Оператор'), ('p', 'Исполнитель')], max_length=1, verbose_name='Роль')),
                ('spent', models.PositiveIntegerField(blank=True, null=True, verbose_name='Затраченное время')),
                ('incoming_date', models.DateTimeField(blank=True, db_column='incomingdate', null=True, verbose_name='Дата поступления')),
                ('completion_date', models.DateTimeField(blank=True, db_column='completiondate', null=True, verbose_name='Дата завершения')),
            ],
            options={
                'verbose_name': 'Участник',
                'verbose_name_plural': 'Участники',
                'db_table': 'sys_workflowparticipant',
            },
        ),
        migrations.CreateModel(
            name='ScriptCommand',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Описание')),
                ('command', models.TextField(verbose_name='Команда для запуска')),
            ],
            options={
                'verbose_name': 'Команда',
                'verbose_name_plural': 'Справочник команд',
                'db_table': 'sys_scriptcommand',
            },
        ),
        migrations.CreateModel(
            name='WorkflowMemo',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Заголовок')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('due_date', models.DateTimeField(verbose_name='Срок исполнения', db_column='duedate', validators=[npf.contrib.common.validators.future_only.FutureOnlyValidator()])),
                ('deadline', models.DateTimeField(blank=True, verbose_name='Крайний срок исполнения', null=True, validators=[npf.contrib.common.validators.future_only.FutureOnlyValidator()])),
                ('why_critical', models.TextField(blank=True, db_column='whycritical', null=True, verbose_name='Почему данная задача является критической')),
                ('task_type', models.CharField(max_length=1, verbose_name='Характер задачи', db_column='tasktype', choices=[('b', 'Ошибка'), ('t', 'Задача'), ('i', 'Улучшение')])),
                ('status', models.CharField(choices=[('o', 'Открыта'), ('r', 'Выполнена'), ('c', 'Закрыта')], default='o', max_length=1, verbose_name='Статус')),
                ('text', models.TextField(verbose_name='Текст задачи')),
                ('estimation', models.CharField(blank=True, max_length=100, null=True, verbose_name='Временная оценка')),
                ('employment_rate', models.PositiveIntegerField(verbose_name='Процент занятости исполнителя', db_column='employmentrate', validators=[django.core.validators.MaxValueValidator(100)])),
                ('complete', models.BooleanField(default=False, verbose_name='Завершить')),
                ('current_participant', models.ForeignKey(editable=False, to='workflow.Participant', blank=True, db_column='workflowparticipant_id', null=True, on_delete=django.db.models.deletion.SET_NULL)),
                ('customer', models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL, blank=True, db_column='auth_user_customer_id', null=True)),
            ],
            options={
                'verbose_name': 'Служебная записка',
                'verbose_name_plural': 'Служебные записки',
                'db_table': 'sys_workflowmemo',
            },
        ),
        migrations.CreateModel(
            name='WorkflowProcess',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Название')),
                ('active', models.BooleanField(default=True, verbose_name='Активен')),
                ('document_type', models.ForeignKey(verbose_name='Тип документа', blank=True, to='dict.DocumentType', db_column='documenttype_id', null=True)),
            ],
            options={
                'verbose_name': 'Рабочий процесс',
                'verbose_name_plural': 'Справочник рабочих процессов',
                'db_table': 'sys_workflowprocess',
            },
        ),
        migrations.CreateModel(
            name='WorkflowProcessInstance',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Описание')),
                ('assignment_responsible', models.ForeignKey(verbose_name='Ответственный за назначения', to=settings.AUTH_USER_MODEL, db_column='auth_user_assignmentresponsible_id')),
                ('process', models.ForeignKey(verbose_name='Рабочий процесс', blank=True, to='workflow.WorkflowProcess', db_column='workflowprocess_id', null=True)),
            ],
            options={
                'verbose_name': 'Рабочий процесс',
                'verbose_name_plural': 'Запущенные рабочие процессы',
                'db_table': 'sys_workflowprocessinstance',
            },
        ),
        migrations.CreateModel(
            name='WorkflowTask',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Название задачи')),
                ('order', models.IntegerField(verbose_name='Последовательный номер')),
                ('action_type', models.CharField(max_length=1, verbose_name='Тип действия', db_column='actiontype', choices=[('i', 'Ввод данных'), ('u', 'Редактирование'), ('d', 'Удаление'), ('c', 'Контроль')])),
                ('due_time', models.TimeField(blank=True, db_column='duetime', null=True, verbose_name='Время на выполнение')),
                ('automatic_assignment', models.BooleanField(db_column='automaticassignment', default=False, verbose_name='Автоматическое назначение')),
                ('affects_to_system_date', models.BooleanField(db_column='affectstosystemdate', default=False, verbose_name='Влияет на дату системы')),
                ('version', models.IntegerField(verbose_name='Версия')),
                ('after_close_command', models.ForeignKey(verbose_name='Комманда после завершении', blank=True, to='workflow.ScriptCommand', db_column='scriptcommand_id', null=True)),
                ('content_type', models.ForeignKey(verbose_name='Тип объекта', to='contenttypes.ContentType', db_column='django_content_type_id')),
                ('last_version', models.ForeignKey(verbose_name='Последняя версия', blank=True, to='workflow.WorkflowTask', db_column='workflowtask_lastversion_id', null=True)),
                ('process', models.ForeignKey(verbose_name='Рабочий процесс', to='workflow.WorkflowProcess', db_column='workflowprocess_id')),
                ('user_group', models.ForeignKey(verbose_name='Группа пользователей', to='auth.Group', db_column='auth_group_id')),
            ],
            options={
                'verbose_name': 'Шаблон задачи',
                'verbose_name_plural': 'Справочник задач',
                'db_table': 'sys_workflowtask',
            },
        ),
        migrations.CreateModel(
            name='WorkflowTaskInstance',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('state', models.CharField(choices=[('o', 'Открыта'), ('c', 'Закрыта')], default='o', max_length=1, verbose_name='Статус')),
                ('due_date', models.DateTimeField(blank=True, db_column='duedate', null=True, verbose_name='Срок исполнения')),
                ('opened_at', models.DateTimeField(blank=True, db_column='openedat', null=True, verbose_name='Дата и время создания')),
                ('closed_at', models.DateTimeField(blank=True, db_column='closedat', null=True, verbose_name='Дата и время завершения')),
                ('object_id', models.PositiveIntegerField(blank=True, db_column='objectid', null=True, verbose_name='ID объекта')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType', blank=True, db_column='django_content_type_id', null=True)),
                ('performer', models.ForeignKey(verbose_name='Исполнитель', blank=True, to=settings.AUTH_USER_MODEL, db_column='auth_user_performer_id', null=True)),
                ('process', models.ForeignKey(verbose_name='Экземпляр рабочего процесса', to='workflow.WorkflowProcessInstance', db_column='workflowprocessinstance_id')),
                ('task', models.ForeignKey(verbose_name='Шаблон задачи', to='workflow.WorkflowTask', db_column='workflowtask_id')),
            ],
            options={
                'verbose_name': 'Задача',
                'verbose_name_plural': 'Все задачи',
                'db_table': 'sys_workflowtaskinstance',
            },
        ),
        migrations.AddField(
            model_name='workflowmemo',
            name='process_instance',
            field=models.ForeignKey(verbose_name='Рабочий процесс', blank=True, to='workflow.WorkflowProcessInstance', db_column='workflowprocessinstance_id', null=True),
        ),
        migrations.AddField(
            model_name='workflowmemo',
            name='relatedmemos',
            field=models.ManyToManyField(related_name='relatedmemos_rel_+', blank=True, to='workflow.WorkflowMemo', verbose_name='Связанные задачи'),
        ),
        migrations.AddField(
            model_name='participant',
            name='memo',
            field=models.ForeignKey(verbose_name='Записка', to='workflow.WorkflowMemo', db_column='workflowmemo_id'),
        ),
        migrations.AddField(
            model_name='participant',
            name='user',
            field=models.ForeignKey(verbose_name='Сотрудник', to=settings.AUTH_USER_MODEL, db_column='auth_user_id'),
        ),
        migrations.AddField(
            model_name='attachment',
            name='memo',
            field=models.ForeignKey(verbose_name='Записка', to='workflow.WorkflowMemo', db_column='workflowmemo_id'),
        ),
        migrations.CreateModel(
            name='WorkflowMyTaskInstance',
            fields=[
            ],
            options={
                'verbose_name': 'Задача',
                'verbose_name_plural': 'Мои задачи',
                'proxy': True,
            },
            bases=('workflow.workflowtaskinstance',),
        ),
        migrations.AlterUniqueTogether(
            name='workflowtask',
            unique_together=set([('id', 'order', 'version')]),
        ),
    ]
