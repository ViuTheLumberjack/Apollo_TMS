from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer
import tasks.models

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = tasks.models.Task
        fields = '__all__'

class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = tasks.models.Collection
        fields = '__all__'

class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = tasks.models.Assignment
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
