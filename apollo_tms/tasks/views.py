from rest_framework import viewsets, generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response

from .permissions import IsGroupMember, IsGroupOwner, IsAssignee, CanBeSeen
from .models import Task, Assignment, Collection
import tasks.models as models
import tasks.serializers as serializers
from apollo_account.serializers import GroupMemberIDSerializer
from apollo_account.models import Organization, ApolloUser

from notifications.models import Notification

# Create your views here.
class CollectionViewSet(viewsets.ModelViewSet):
    '''
        Methods to handle Collection CRUD
    '''
    authentication_classes = (TokenAuthentication, )
    
    def get_permissions(self):
        permissions = [IsAuthenticated]
        if self.action == 'retrieve' or self.action == 'list':
            permissions.append(IsGroupMember)
        else:
            permissions.append(IsGroupOwner)

        return [permission() for permission in permissions]
    
    def get_queryset(self):
        return Collection.objects.filter(owner__in=Organization.objects.filter(members=self.request.user))
    
    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.CollectionListSerializer
        elif self.action == 'retrieve':
            return serializers.CollectionDetailSerializer
        else:
            return serializers.CollectionCreateSerializer
    
    def create(self, request, *args, **kwargs):
        '''
            Create a new collection, and send a notification to all members of the organization
        '''
        collection = models.Collection.objects.create(name = request.data['name'], description = request.data['description'], owner_id = request.data['owner_id'])
        collection.save()
        for member in Organization.objects.get(pk=request.data['owner_id']).members.all():
            Notification.objects.create(
                type = 'N',
                description = f'{f"{request.user.first_name} {request.user.last_name}" if request.user.first_name else request.user.username} created a new collection: {collection.name}',
                user = member,
                collection = collection,
            )
        serializer = serializers.CollectionDetailSerializer(collection)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        """
            Update a collection, and send a notification to all members of the organization
        """
        collection = self.get_object()
        old_name = collection.name
        collection.name = request.data['name']
        collection.description = request.data['description']
        collection.save()
        for member in Organization.objects.get(pk=request.data['owner_id']).members.all():
            Notification.objects.create(
                type = 'U',
                description = f'{f"{request.user.first_name} {request.user.last_name}" if request.user.first_name else request.user.username} updated a collection: {old_name}',
                user = member,
                collection = collection,
            )
        serializer = serializers.CollectionDetailSerializer(collection)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        """
            Delete a collection, and send a notification to all members of the organization
        """
        collection = self.get_object()
        old_name = collection.name
        collection.delete()
        for member in Organization.objects.get(pk=request.data['owner_id']).members.all():
            Notification.objects.create(
                type = 'D',
                description = f'{f"{request.user.first_name} {request.user.last_name}" if request.user.first_name else request.user.username} deleted a collection: {old_name}',
                user = member,
            )
        return Response(data={'message': 'Collection deleted'}, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        """
            List all collections the user is a member of
        """
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        """
            Retrieve a collection if the user can see it
        """
        return super().retrieve(request, *args, **kwargs)


class TaskViewSet(viewsets.ModelViewSet):
    """
        Methods to handle Task CRUD
    """
    queryset = models.Task.objects.all()
    authentication_classes = (TokenAuthentication, )

    def get_serializer_class(self, *args, **kwargs):
        if self.action == 'assign':
            return GroupMemberIDSerializer
        elif self.action == 'retrieve' or self.action == 'list':
            return serializers.TaskPolymorphicSerializer
        else:
            return serializers.TaskInsertPolymorphicSerializer
    
    @permission_classes((IsGroupOwner, ))
    def create(self, request, *args, **kwargs):
        """
            Create a new task, and send a notification to all members of the organization.
            The DeadlineTask, RecurrentTask and OneTimeTask have extra attributes that need to be set:
            - DeadlineTask: due_date
            - RecurrentTask: end_date, frequency
            - OneTimeTask: None
        """
        # check if the task has a parent and if the parent has a parent i.e. if the task is a subtask of a subtask. If so, return an error
        if 'parent_id' in request.data:
            parent = Task.objects.get(pk=request.data['parent_id'])
            if parent.parent is not None:
                return Response(data={'message': 'A task cannot be a subtask of a subtask'}, status=status.HTTP_400_BAD_REQUEST)

        # create task
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        # add collection to task
        instance.collection = Collection.objects.get(pk=kwargs['collection_id'])
        instance.save()
        # If the task has a parent, add it to the parent's subtasks
        serializer = serializers.TaskPolymorphicSerializer(instance)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @permission_classes((CanBeSeen, ))
    def list(self, request, *args, **kwargs):
        """
            List all tasks in a collection
        """
        queryset = Task.objects.filter(collection__id=self.kwargs['collection_id'], parent__isnull=True)
        serializer = serializers.TaskPolymorphicSerializer(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @permission_classes((CanBeSeen, ))
    def retrieve(self, request, *args, **kwargs):
        """
            Get the tasks in a collection given id
        """
        queryset = Task.objects.filter(collection__id=self.kwargs['collection_id'], parent__isnull=True, id=self.kwargs['pk'])
        serializer = serializers.TaskPolymorphicSerializer(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], url_path='status')
    @permission_classes((IsAssignee | CanBeSeen, ))
    def status(self, request, *args, **kwargs):
        """
            Update the status of a task. On completion, send a notification to owner of the collection
        """
        task = self.get_object()
        task.task_status = request.data['status']
        if task.task_status == 'C':
            task.progress = 100.0
            # If the task has a parent, update the parent's progress
            if task.parent:
                parent = task.parent
                parent.progress = parent.progress + (100.0 / len(Task.objects.filter(parent=parent)))
                parent.status = 'C' if parent.progress == 100.0 else 'P'
                parent.save()


            collection_owner = task.collection.owner.owner
            Notification.objects.create(
                type = 'C',
                description = f'{f"{request.user.first_name} {request.user.last_name}" if request.user.first_name else request.user.username} completed a task: {task.title}',
                user = collection_owner,
                task = task,
            )
        task.save()

        serializer = serializers.TaskPolymorphicSerializer(task)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], url_path='assign')
    @permission_classes((IsGroupOwner, ))
    def assign(self, request, *args, **kwargs):
        """
            Assign a task to a user, and send a notification to the user. Can be done by owner
        """
        assert 'user_id' in request.data, 'user_id not provided'
        
        task = self.get_object()
        user = ApolloUser.objects.get(id=request.data['user_id'])
        assignment = Assignment.objects.create(task=task, users=user)

        Notification.objects.create(
            type = 'A',
            description = f'{f"{request.user.first_name} {request.user.last_name}" if request.user.first_name else request.user.username} assigned you a task: {task.title}',
            user = user,
            task = task,
        )
        assignment.save()
        return Response(data={'message': 'Task assigned'}, status=status.HTTP_200_OK)

    @permission_classes((IsGroupOwner, ))
    def destroy(self, request, *args, **kwargs):
        """
            Delete a task, and send a notification to all members of the organization
        """
        task = self.get_object()
        old_title = task.title
        task.delete()
        for member in Organization.objects.get(pk=request.data['owner_id']).members.all():
            Notification.objects.create(
                type = 'D',
                description = f'{f"{request.user.first_name} {request.user.last_name}" if request.user.first_name else request.user.username} deleted a task: {old_title}',
                user = member,
            )
        return Response(data={'message': 'Task deleted'}, status=status.HTTP_200_OK)

    @permission_classes((IsGroupOwner, ))
    def update(self, request, *args, **kwargs):
        """
            Update a task, and send a notification to all members of the organization
        """
        task = self.get_object()
        old_title = task.title
        task.title = request.data['title']
        task.description = request.data['description']
        task.save()
        for member in Organization.objects.get(pk=request.data['owner_id']).members.all():
            Notification.objects.create(
                type = 'U',
                description = f'{f"{request.user.first_name} {request.user.last_name}" if request.user.first_name else request.user.username} updated a task: {old_title}',
                user = member,
                task = task,
            )
        serializer = serializers.TaskPolymorphicSerializer(task)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @permission_classes((IsGroupOwner, ))
    def partial_update(self, request, *args, **kwargs):
        return self.update(self, request, *args, **kwargs)


class PersonalTasksView(generics.ListAPIView):
    """
        List all tasks assigned to the user, or tasks in collections the user is a member of.
    """
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    serializer_class = serializers.TaskPolymorphicSerializer

    def get_queryset(self):
        return Task.objects.filter(pk__in=Assignment.objects.filter(users__id=self.request.user.id), parent__isnull=True) | Task.objects.filter(collection__in=Collection.objects.filter(owner__in=Organization.objects.filter(members=self.request.user)), parent__isnull=True)