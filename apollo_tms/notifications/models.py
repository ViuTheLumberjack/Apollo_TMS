from django.db import models

from apollo_account.models import ApolloUser
from tasks.models import Task, Collection

# Create your models here.
class Notification(models.Model):
    '''
        A notification is a message sent to a user to inform him of a change in the system.
        It can be of different types, listed in the Type class.

        Not very elegant because it holds a reference to a task or a collection which are assigned only one at a time.
        A dynamic reference would be better, but this solution is simple and gets the job done.
    '''
    class Type(models.TextChoices):
        NEW = 'N', 'Added'
        UPDATE = 'U', 'Updated'
        ASSIGN = 'A', 'Assigned'
        COMPLETE = 'C', 'Completed'
        DELETE = 'D', 'Deleted'

    user = models.ForeignKey(ApolloUser, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, null=True)
    description = models.TextField()
    type = models.CharField(max_length=1, choices=Type.choices, default='N')
    read = models.BooleanField(default=False)