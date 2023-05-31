# Generated by Django 4.2.1 on 2023-05-31 15:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_alter_task_options_remove_assignment_group_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='deletable',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='collection',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tasks.collection'),
        ),
        migrations.AlterField(
            model_name='task',
            name='subtasks',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='tasks.task'),
        ),
    ]
