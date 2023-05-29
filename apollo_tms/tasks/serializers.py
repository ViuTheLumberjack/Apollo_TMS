from rest_framework import serializers
import tasks.models

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = tasks.models.Task
        fields = '__all__'