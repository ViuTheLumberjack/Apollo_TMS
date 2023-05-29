from django.contrib.auth import login
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions, views, status
from rest_framework.authtoken.models import Token

from . import serializers
# Create your views here.

class LoginView(views.APIView):
    # This view should be accessible also for unauthenticated users.
    permission_classes = (permissions.AllowAny,)

    @method_decorator(csrf_exempt, name='post')
    def post(self, request, format=None):
        serializer = serializers.LoginSerializer(data=self.request.data,
            context={'request': self.request })
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        token, created = Token.objects.get_or_create(user=request.user)
        return JsonResponse({"success": "True", "token": token.key}, status=status.HTTP_200_OK)