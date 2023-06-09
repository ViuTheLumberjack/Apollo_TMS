from django.db import models
from polymorphic.models import PolymorphicModel
from apollo_account.models import ApolloUser, Organization

# Create your models here.
class Collection(models.Model):
    """
    Collection model
    """
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(Organization, on_delete=models.CASCADE)
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
    class Status(models.TextChoices):
        NEW = 'N', 'New'
        IN_PROGRESS = 'P', 'In Progress'
        COMPLETED = 'C', 'Completed'

    title = models.CharField(max_length=255)
    description = models.TextField()
    task_status = models.CharField(max_length=1, choices=Status.choices, default='N')
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    progress = models.FloatField(default=0.0)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
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
    users = models.ForeignKey(ApolloUser, on_delete=models.CASCADE)
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