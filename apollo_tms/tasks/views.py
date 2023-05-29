from rest_framework import viewsets, permissions, generics
from rest_framework.authentication import TokenAuthentication
import tasks.models as models
import tasks.serializers as serializers

# Create your views here.
class TaskViewSet(generics.ListAPIView):
    queryset = models.Task.objects.all()
    serializer_class = serializers.TaskSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (permissions.IsAuthenticated,)

class TaskDetailViewSet(generics.RetrieveAPIView):
    queryset = models.Task.objects.all()
    serializer_class = serializers.TaskSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (permissions.IsAuthenticated,)