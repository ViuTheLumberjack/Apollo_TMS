from django.db import models
from polymorphic.models import PolymorphicModel
from apollo_account.models import User
from django.contrib.auth.models import Group

# Create your models here.
class Collection(models.Model):
    """
    Collection model
    """
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(Group, on_delete=models.CASCADE)
    deletable = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'collections'
        ordering = ['-created_at']
        verbose_name = 'Collection'
        verbose_name_plural = 'Collections'

class Task(PolymorphicModel):
    """
    Task model
    """
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = [
        ('N', 'New'),
        ('P', 'In Progress'),
        ('C', 'Completed'),

    ]
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    progress = models.FloatField(default=0.0)
    subtasks = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'task'
        ordering = ['-created_at']
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'

class Assignment(models.Model):
    """
    Assignment model
    """
    users = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.task} assigned to {self.users}'

    class Meta:
        db_table = 'assignments'
        ordering = ['-created_at']
        verbose_name = 'Assignment'
        verbose_name_plural = 'Assignments'

class RecurrentTask(Task):
    """
    Recurrent Task model
    """
    end_date = models.DateTimeField(null=True, blank=True)
    frequency = models.CharField(max_length=255)

    class Meta:
        db_table = 'recurrent-tasks'
        ordering = ['-created_at']
        verbose_name = 'Recurrent Task'
        verbose_name_plural = 'Recurrent Tasks'

class OneTimeTask(Task):
    """
    One Time Task model
    """

    class Meta:
        db_table = 'one-time-tasks'
        ordering = ['-created_at']
        verbose_name = 'One Time Task'
        verbose_name_plural = 'One Time Tasks'

class DeadlineTask(Task):
    """
    Deadline Task model
    """
    due_date = models.DateTimeField()

    class Meta:
        db_table = 'deadline-tasks'
        ordering = ['-created_at']
        verbose_name = 'Deadline Task'
        verbose_name_plural = 'Deadline Tasks'