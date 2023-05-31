from rest_framework import serializers
from django.contrib.auth import authenticate
from dj_rest_auth.registration.serializers import RegisterSerializer
from django.contrib.auth.models import Group

class ApolloRegisterSerializer(RegisterSerializer):
    # this method is called at save
    def custom_signup(self, request, user):
        group = Group.objects.create(name=f'{user.username}_group')
        user.groups.add(group)
        user.save()