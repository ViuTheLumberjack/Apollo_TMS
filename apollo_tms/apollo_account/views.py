from django.core.exceptions import PermissionDenied
from rest_framework import permissions, status, viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.decorators import action

from .permissions import IsOwnerOrSelf
from . import models as models
from . import serializers as serializers

from notifications.models import Notification

# Create your views here.

class UserViewSet(viewsets.mixins.RetrieveModelMixin, 
                  viewsets.mixins.UpdateModelMixin,
                  viewsets.mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    '''
        Admin users only viewset for user management
    '''
    queryset = models.ApolloUser.objects.all()
    authentication_classes = (TokenAuthentication, )
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser)  

    def get_serializer_class(self):
        if self.action in ['retrieve', 'destroy']:
            return serializers.UserSerializer
        else:
            return serializers.UserDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        '''
            Get the user details. Admin Only
        '''
        return super().retrieve(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        '''
            Modify user details. Admin Only
        '''
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        '''
            Delete user details. Admin Only
        '''
        return super().destroy(request, *args, **kwargs)


class GroupViewSet(viewsets.ModelViewSet):
    queryset = models.Organization.objects.all()
    authentication_classes = (TokenAuthentication, )

    def get_serializer_class(self):
        if self.action in ['create', 'list']:
            return serializers.GroupSerializer
        else:
            return serializers.GroupDetailSerializer
        
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create', 'list', 'discover']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsOwnerOrSelf, permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        '''
            Create a new group. Owner is the user who requested the creation, 
            every new group has a default collection.
        '''
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)
    
    def list(self, request, *args, **kwargs):
        '''
            List of groups owned by the user
        '''
        queryset = models.Organization.objects.filter(owner=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='discover')
    def discover(self, request, *args, **kwargs):
        '''
            List of groups that the user can join, 
            i.e. groups that are public or invite only and the user is not a member of
        '''
        queryset = models.Organization.objects.filter(group_visibility__in=['P', 'I']).exclude(owner=request.user) & models.Organization.objects.exclude(members=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    def retrieve(self, request, *args, **kwargs):
        '''
            Get the group details
        '''
        return super().retrieve(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        '''
            Modify the group details
        '''
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        '''
            Delete the group
        '''
        return super().destroy(request, *args, **kwargs)
    

class GroupMembersViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = models.Organization.objects.all()
    authentication_classes = (TokenAuthentication, )
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        if self.action in ['create', 'destroy']:
            return serializers.GroupMemberIDSerializer
        elif self.action == 'list':
            return serializers.UserSerializer
        else:
            return serializers.GroupInviteSerializer
        
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create':
            permission_classes = [IsOwnerOrSelf, permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        # owner can add members to the group
        group = models.Organization.objects.get(pk=kwargs['group_id'])
        user = models.ApolloUser.objects.get(pk=request.data['new_member'])
        if user is None:
            raise PermissionDenied('User does not exist')
        elif user == group.owner:
            raise PermissionDenied('User is already the owner of the group')
        elif user in group.members.all():
            raise PermissionDenied('User is already a member of the group')
        
        group.members.add(user)
        group.save()
        serializer = self.get_serializer(group)
        
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'], url_path='join')
    def invite(self, request, *args, **kwargs):
        group = models.Organization.objects.get(pk=kwargs['group_id'])
        if group.group_visibility == 'I':
            assert 'invite_token' in request.data
            if group.invite_token != request.data['invite_token']:
                raise serializers.ValidationError('Invalid invite token')
        elif group.group_visibility == 'H':
            raise serializers.ValidationError('Group is hidden')
        group.members.add(request.user)
        group.save()
        # create a notification for the owner
        Notification.objects.create(
            user = group.owner,
            type = 'N',
            description = f'{request.user.email} joined the group {group.name}',
            task = None,
            collection = None,
        )
        
        return Response(data={'message': f'You Joined the group {group.name}'}, status=status.HTTP_201_CREATED)
    
    def list(self, request, *args, **kwargs):
        # get the list of members of the group
        queryset = models.Organization.objects.get(pk=kwargs['group_id']).members.all()
        serializer = self.get_serializer(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        # owner can remove members from the group or self can leave the group
        group = models.Organization.objects.get(pk=kwargs['group_id'])
        if group.owner == request.user:
            # owner can remove members from the group
            if group.owner.id == kwargs['pk']: ### TODO: WHY THE FUCK DON'T YOU WORK
                raise PermissionDenied('Owner cannot remove self from group')

            user_to_remove = models.ApolloUser.objects.get(pk=kwargs['pk'])
            group.members.remove(user_to_remove)
            group.save()
            return Response(data={'message': f'You removed {user_to_remove.email} from the group'}, status=status.HTTP_204_NO_CONTENT)
        elif request.user in group.members.all():
            # self can leave the group
            
            group.members.remove(request.user)
            group.save()
            return Response(data={'message': 'You have left the group'}, status=status.HTTP_204_NO_CONTENT)
    