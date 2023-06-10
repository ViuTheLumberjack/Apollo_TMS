from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.HyperlinkedModelSerializer):
    object = serializers.SerializerMethodField()

    def get_object(self, obj):
        if obj.task:
            return obj.task.title
        elif obj.collection:
            return obj.collection.name
        else:
            return None

    class Meta:
        model = Notification
        fields = ['id', 'type', 'description', 'read', 'object']