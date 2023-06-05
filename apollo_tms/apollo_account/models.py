import random, string
from django.db import models
from django.contrib.auth.models import AbstractUser, Group

class ApolloUser(AbstractUser):
    pass

class Organization(Group):
    class Visibility(models.TextChoices):
        PRIVATE = 'H', 'Hidden'
        PUBLIC = 'P', 'Public'
        INVITE_ONLY = 'I', 'Invite Only'
    
    group_visibility = models.CharField(max_length=1, choices=Visibility.choices, default='H')
    owner = models.ForeignKey(ApolloUser, on_delete=models.CASCADE, related_name='owner')
    members = models.ManyToManyField(ApolloUser, related_name='members')
    invite_token = models.CharField(max_length=100, default=(''.join(random.choices(string.ascii_uppercase + string.digits, k=15))))

    def __str__(self):
        return self.pk
