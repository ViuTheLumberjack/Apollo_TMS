from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from rest_framework import permissions, status
from rest_framework.authentication import TokenAuthentication
from rest_framework import viewsets, mixins
from rest_framework.decorators import action, permission_classes

from .permissions import IsOwnerOrSelf
from . import models as models
from . import serializers as serializers
# Create your views here.

class UserViewSet(viewsets.mixins.RetrieveModelMixin, 
                  viewsets.mixins.UpdateModelMixin,
                  viewsets.mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    queryset = models.ApolloUser.objects.all()
    authentication_classes = (TokenAuthentication, )
    permission_classes = (permissions.IsAuthenticated)  
    serializer_class = serializers.UserSerializer

class GroupViewSet(viewsets.ModelViewSet):
    queryset = models.Organization.objects.all()
    authentication_classes = (TokenAuthentication, )
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrSelf)

    def get_serializer_class(self):
        if self.action in ['create', 'list']:
            return serializers.GroupSerializer
        else:
            return serializers.GroupDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return JsonResponse(data=serializer.data, status=status.HTTP_201_CREATED)
    
    def list(self, request, *args, **kwargs):
        # get the list of public and invite only and own organizations
        queryset = models.Organization.objects.filter(owner=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return JsonResponse(data=serializer.data, status=status.HTTP_200_OK, safe=False)
    
    @action(detail=False, methods=['get'], url_path='discover')
    def discover(self, request, *args, **kwargs):
        # get the list of public organizations
        queryset = models.Organization.objects.filter(group_visibility__in=['P', 'I']).exclude(owner=request.user) & models.Organization.objects.exclude(members=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return JsonResponse(data=serializer.data, status=status.HTTP_200_OK, safe=False)
    

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
        
        return JsonResponse(data=serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'], url_path='join')
    def invite(self, request, *args, **kwargs):
        group = models.Organization.objects.get(pk=kwargs['group_id'])
        if group.invite_token != request.data['invite_token']:
            raise serializers.ValidationError('Invalid invite token')
        group.members.add(request.user)
        group.save()
        return JsonResponse(data={'message': f'You Joined the group {group.name}'}, status=status.HTTP_201_CREATED)
    
    def list(self, request, *args, **kwargs):
        # get the list of members of the group
        queryset = models.Organization.objects.get(pk=kwargs['group_id']).members.all()
        serializer = self.get_serializer(queryset, many=True)
        return JsonResponse(data=serializer.data, status=status.HTTP_200_OK, safe=False)
    
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
            return JsonResponse(data={'message': f'You removed {user_to_remove.email} from the group'}, status=status.HTTP_204_NO_CONTENT)
        elif request.user in group.members.all():
            # self can leave the group
            
            group.members.remove(request.user)
            group.save()
            return JsonResponse(data={'message': 'You have left the group'}, status=status.HTTP_204_NO_CONTENT)
    