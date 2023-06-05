from rest_framework import viewsets, generics
from rest_framework.authentication import TokenAuthentication
import tasks.models as models
import tasks.serializers as serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.http import JsonResponse

from .permissions import IsGroupMember, IsGroupOwner
from .models import Task, Assignment
from apollo_account.models import Organization
from apollo_account.serializers import GroupMemberIDSerializer

from notifications.models import Notification

# Create your views here.
class CollectionViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication, )
    
    def get_permissions(self):
        permissions = [IsAuthenticated]

        if self.action == 'retrieve' or self.action == 'list':
            permissions.append(IsGroupMember)
        else:
            permissions.append(IsGroupOwner)

        return [permission() for permission in permissions]
    
    def get_queryset(self):
        return models.Collection.objects.filter(owner__in=Organization.objects.filter(members=self.request.user))
    
    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.CollectionListSerializer
        elif self.action == 'retrieve':
            return serializers.CollectionDetailSerializer
        elif self.action == 'create':
            return serializers.CollectionCreateSerializer
        return serializers.CollectionListSerializer
    
    def create(self, request, *args, **kwargs):
        collection = models.Collection.objects.create(name = request.data['name'], description = request.data['description'], owner_id = request.data['owner_id'])
        collection.save()
        serializer = serializers.CollectionDetailSerializer(collection)
        return JsonResponse(data=serializer.data, status=status.HTTP_200_OK, safe=False)

class TaskViewSet(viewsets.ModelViewSet):
    queryset = models.Task.objects.all()
    authentication_classes = (TokenAuthentication, )

    def get_serializer_class(self, *args, **kwargs):
        if self.action == 'assign':
            return serializers.GroupMemberIDSerializer
        else:
            return serializers.TaskPolymorphicSerializer

    def get_permissions(self):
        permissions = [IsAuthenticated]

        if self.action == 'retrieve' or self.action == 'list' or self.action == 'status':
            permissions.append(IsGroupMember)
        else:
            permissions.append(IsGroupOwner)

        return [permission() for permission in permissions]
    
    def list(self, request, *args, **kwargs):
        queryset = Task.objects.filter(collection__id=self.kwargs['collection_id'])
        serializer = serializers.TaskPolymorphicSerializer(queryset, many=True)
        return JsonResponse(data=serializer.data, status=status.HTTP_200_OK, safe=False)
    
    @action(detail=True, methods=['post'], url_path='status')
    def status(self, request, *args, **kwargs):
        task = self.get_object()
        task.task_status = request.data['status']
        if task.task_status == 'C':
            task.progress = 100.0
            father = Task.objects.get(subtasks=task)
            while father.exists():
                father.progress = (100.0 / father.subtasks.count())
                father.save()
                father = Task.objects.get(subtasks=father)

        task.save()
        serializer = serializers.TaskPolymorphicSerializer(task)
        return JsonResponse(data=serializer.data, status=status.HTTP_200_OK, safe=False)
    
    @action(detail=True, methods=['post'], url_path='assign')
    def assign(self, request, *args, **kwargs):
        task = self.get_object()
        user = Organization.objects.get(members__id=request.data['user_id'])
        assignment = Assignment.objects.create(task=task, user=user)
        assignment.save()

class PersonalTasks(generics.ListAPIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    serializer_class = serializers.TaskPolymorphicSerializer

    def get_queryset(self):
        return Task.objects.filter(pk__in=Assignment.objects.filter(users__id=self.request.user.id)) | Task.objects.filter(collection__in=self.request.user.collections.all())