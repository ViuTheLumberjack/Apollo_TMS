from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action

from .serializers import NotificationSerializer
from .permissions import IsAssignee

# Create your views here.
class NotificationView(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    '''
        View for notifications, allows to get a list of notifications, not read notifications 
        and mark a notification as read.
    '''
    serializer_class = NotificationSerializer
    permissions = (IsAuthenticated, )
    authentication_classes = (TokenAuthentication, )

    def get_queryset(self):
        queryset = self.request.user.notifications.all()
        if self.request.action == 'not_read':
            queryset = queryset.filter(read=False)
        
        return queryset    

    @action(methods=['GET'], detail=False, url_path='notread')
    def not_read(self, request, *args, **kwargs):
       ''''
            List of not read notifications
       '''
       return super().list(request, *args, **kwargs) 

    @action(methods=['POST'], detail=True, url_path='read', permissions=(IsAssignee, ))
    def read(self, request, *args, **kwargs):
        '''
            Mark a notification as read
        '''
        notification = self.get_object()
        notification.read = True
        notification.save()
        return super().retrieve(request, *args, **kwargs)
