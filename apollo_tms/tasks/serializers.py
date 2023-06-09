from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer
import tasks.models


class CollectionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = tasks.models.Collection
        fields = ['id', 'name', 'description', 'owner_id']

class TaskInsertSerializer(serializers.ModelSerializer):
    class Meta:
        model = tasks.models.Task
        fields = ['id', 'title', 'progress', 'task_status', 'description', 'parent']
        
class RecurrentTaskInsertSerializer(serializers.ModelSerializer):
    class Meta:
        model = tasks.models.RecurrentTask
        fields = ['id', 'title', 'progress', 'task_status', 'description', 'parent', 'end_date', 'frequency']

class OneTimeTaskInsertSerializer(serializers.ModelSerializer):
    class Meta:
        model = tasks.models.OneTimeTask
        fields = ['id', 'title', 'progress', 'task_status', 'description', 'parent']

class DeadlineTaskInsertSerializer(serializers.ModelSerializer):
    class Meta:
        model = tasks.models.DeadlineTask
        fields = ['id', 'title', 'progress', 'task_status', 'description', 'parent', 'due_date']

class TaskInsertPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        tasks.models.Task: TaskInsertSerializer,
        tasks.models.DeadlineTask: DeadlineTaskInsertSerializer,
        tasks.models.RecurrentTask: RecurrentTaskInsertSerializer,
        tasks.models.OneTimeTask: OneTimeTaskInsertSerializer
}   

class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = tasks.models.Assignment
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):
    subtasks = serializers.SerializerMethodField(read_only=True, source='get_subtasks')
    collection = serializers.PrimaryKeyRelatedField(read_only=True, many=False)
    
    def get_subtasks(self, instance):
        qset = tasks.models.Task.objects.filter(parent__id=instance.id)
        return TaskInsertPolymorphicSerializer(qset, many=True).data

    class Meta:
        model = tasks.models.Task
        fields = ['id', 'title', 'description', 'task_status', 'created_at', 'start_date', 'updated_at', 'progress', 'subtasks', 'collection']
        
class RecurrentTaskSerializer(serializers.ModelSerializer):
    subtasks = serializers.SerializerMethodField(read_only=True, source='get_subtasks')
    collection = serializers.PrimaryKeyRelatedField(read_only=True, many=False)

    def get_subtasks(self, instance):
        qset = tasks.models.Task.objects.filter(parent__id=instance.id)
        return TaskInsertPolymorphicSerializer(qset, many=True).data

    class Meta:
        model = tasks.models.RecurrentTask
        fields = ['id', 'title', 'description', 'task_status', 'created_at', 'start_date', 'updated_at', 'progress', 'subtasks', 'collection', 'end_date', 'frequency']

class OneTimeTaskSerializer(serializers.ModelSerializer):
    subtasks = serializers.SerializerMethodField(read_only=True, source='get_subtasks')
    collection = serializers.PrimaryKeyRelatedField(read_only=True, many=False)
    
    def get_subtasks(self, instance):
        qset = tasks.models.Task.objects.filter(parent__id=instance.id)
        return TaskInsertPolymorphicSerializer(qset, many=True).data

    class Meta:
        model = tasks.models.OneTimeTask
        fields = ['id', 'title', 'description', 'task_status', 'created_at', 'start_date', 'updated_at', 'progress', 'subtasks', 'collection']

class DeadlineTaskSerializer(serializers.ModelSerializer):
    subtasks = serializers.SerializerMethodField(read_only=True, source='get_subtasks')
    collection = serializers.PrimaryKeyRelatedField(read_only=True, many=False)
    
    def get_subtasks(self, instance):
        qset = tasks.models.Task.objects.filter(parent__id=instance.id)
        return TaskInsertPolymorphicSerializer(qset, many=True).data

    class Meta:
        model = tasks.models.DeadlineTask
        fields = ['id', 'title', 'description', 'task_status', 'created_at', 'start_date', 'updated_at', 'progress', 'subtasks', 'collection', 'due_date']

class TaskPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        tasks.models.Task: TaskSerializer,
        tasks.models.DeadlineTask: DeadlineTaskSerializer,
        tasks.models.RecurrentTask: RecurrentTaskSerializer,
        tasks.models.OneTimeTask: OneTimeTaskSerializer
    }

class CollectionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = tasks.models.Collection
        fields = ['id', 'name', 'description', 'created_at']

class CollectionDetailSerializer(serializers.ModelSerializer):
    tasks = TaskPolymorphicSerializer(many=True, read_only=True)

    class Meta:
        model = tasks.models.Collection
        fields = ['id', 'name', 'description', 'created_at', 'tasks']