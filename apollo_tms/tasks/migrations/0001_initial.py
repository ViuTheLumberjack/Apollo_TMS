# Generated by Django 4.2.1 on 2023-06-06 18:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('apollo_account', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deletable', models.BooleanField(default=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apollo_account.organization')),
            ],
            options={
                'verbose_name': 'Collection',
                'verbose_name_plural': 'Collections',
                'db_table': 'collections',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('task_status', models.CharField(choices=[('N', 'New'), ('P', 'In Progress'), ('C', 'Completed')], default='N', max_length=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('start_date', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('progress', models.FloatField(default=0.0)),
                ('collection', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tasks.collection')),
                ('polymorphic_ctype', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_%(app_label)s.%(class)s_set+', to='contenttypes.contenttype')),
                ('subtasks', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tasks.task')),
            ],
            options={
                'verbose_name': 'Task',
                'verbose_name_plural': 'Tasks',
                'db_table': 'task',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='DeadlineTask',
            fields=[
                ('task_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='tasks.task')),
                ('due_date', models.DateTimeField()),
            ],
            options={
                'verbose_name': 'Deadline Task',
                'verbose_name_plural': 'Deadline Tasks',
                'db_table': 'deadline-tasks',
                'ordering': ['-created_at'],
            },
            bases=('tasks.task',),
        ),
        migrations.CreateModel(
            name='OneTimeTask',
            fields=[
                ('task_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='tasks.task')),
            ],
            options={
                'verbose_name': 'One Time Task',
                'verbose_name_plural': 'One Time Tasks',
                'db_table': 'one-time-tasks',
                'ordering': ['-created_at'],
            },
            bases=('tasks.task',),
        ),
        migrations.CreateModel(
            name='RecurrentTask',
            fields=[
                ('task_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='tasks.task')),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('frequency', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Recurrent Task',
                'verbose_name_plural': 'Recurrent Tasks',
                'db_table': 'recurrent-tasks',
                'ordering': ['-created_at'],
            },
            bases=('tasks.task',),
        ),
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tasks.task')),
                ('users', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Assignment',
                'verbose_name_plural': 'Assignments',
                'db_table': 'assignments',
                'ordering': ['-created_at'],
            },
        ),
    ]
