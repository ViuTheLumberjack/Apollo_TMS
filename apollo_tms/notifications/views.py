from rest_framework import ListViewAPI
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action

from .serializers import NotificationSerializer
from .permissions import IsAssignee

# Create your views here.
class NotificationView(ListViewAPI):
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
       return super().list(request, *args, **kwargs) 

    @action(methods=['GET'], detail=True, url_path='read', permissions=(IsAssignee, ))
    def read(self, request, *args, **kwargs):
        notification = self.get_object()
        notification.read = True
        notification.save()
        return super().retrieve(request, *args, **kwargs)
