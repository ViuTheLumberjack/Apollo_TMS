from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.HyperlinkedModelSerializer):
    object = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['type', 'description', 'read', 'object']