from django.db import models

from apollo_account.models import ApolloUser
from tasks.models import Task

# Create your models here.
class Notification(models.Model):
    class Type(models.TextChoices):
        NEW = 'N', 'Added'
        UPDATE = 'U', 'Updated'
        ASSIGN = 'A', 'Assigned'
        COMPLETE = 'C', 'Completed'
        DELETE = 'D', 'Deleted'

    user = models.ForeignKey(ApolloUser, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    description = models.TextField()
    type = models.CharField(max_length=1, choiches=Type.choices)
    read = models.BooleanField(default=False)