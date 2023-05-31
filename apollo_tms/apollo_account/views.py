from django.contrib.auth import login
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions, views, status
from rest_framework.authtoken.models import Token

from . import serializers
# Create your views here.