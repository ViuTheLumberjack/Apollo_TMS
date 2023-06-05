from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import ApolloUser

admin.site.register(ApolloUser, UserAdmin)