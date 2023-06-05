from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer
import tasks.models


class CollectionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = tasks.models.Collection
        fields = ['name', 'description', 'owner_id']

class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = tasks.models.Assignment
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = tasks.models.Task
        fields = '__all__'
        
class RecurrentTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = tasks.models.RecurrentTask
        fields = '__all__'

class OneTimeTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = tasks.models.OneTimeTask
        fields = '__all__'

class DeadlineTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = tasks.models.DeadlineTask
        fields = '__all__'

class TaskPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        tasks.models.Task: TaskSerializer,
        tasks.models.DeadlineTask: DeadlineTaskSerializer,
        tasks.models.RecurrentTask: RecurrentTaskSerializer,
        tasks.models.OneTimeTask: OneTimeTaskSerializer
}   

class CollectionListSerializer(serializers.ModelSerializer):
    # open_tasks = serializers.SerializerMethodField()
    class Meta:
        model = tasks.models.Collection
        fields = ['id', 'name', 'description', 'created_at']

class CollectionDetailSerializer(serializers.ModelSerializer):
    tasks = TaskPolymorphicSerializer(many=True, read_only=True)
    #open_tasks = serializers.SerializerMethodField()

    class Meta:
        model = tasks.models.Collection
        fields = ['id', 'name', 'description', 'created_at', 'tasks']