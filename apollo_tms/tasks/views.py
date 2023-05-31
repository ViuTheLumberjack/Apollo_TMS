from rest_framework import viewsets, permissions, generics
from rest_framework.authentication import TokenAuthentication
import tasks.models as models
import tasks.serializers as serializers
from rest_framework.decorators import action

# Create your views here.
class TaskViewSet(viewsets.ModelViewSet):
    queryset = models.Task.objects.all()
    serializer_class = serializers.TaskPolymorphicSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (permissions.IsAuthenticated,)