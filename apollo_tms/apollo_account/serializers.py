from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework.fields import CurrentUserDefault

from .models import Organization, ApolloUser
from tasks.models import Collection

# this class is used to override the default dj_rest_auth registration serializer
class ApolloRegisterSerializer(RegisterSerializer):
    # this method is called at save
    def custom_signup(self, request, user):
        user.save()
        group = Organization.objects.create(name=f'{user.username}_group', owner_id=user.id)
        group.members.add(user)
        user.save()
        group.save()
        # create a default collection for the user
        collection = Collection.objects.create(name=f'{user.username}\'s collection', owner_id=group.id, deletable=False)
        collection.save()

# classes below are used to serialize the Users
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ApolloUser
        fields = ['id', 'url', 'username', 'email']

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApolloUser
        fields = '__all__'

# classes below are used to serialize the Groups
class GroupDetailSerializer(serializers.HyperlinkedModelSerializer):
    owner = UserSerializer(many=False, read_only=True)
    members = UserSerializer(many=True, read_only=True)
    
    class Meta:
        model = Organization
        fields = ['id', 'name', 'group_visibility', 'invite_token', 'owner', 'members', 'url']

class GroupSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True, default=CurrentUserDefault())

    def create(self, validated_data):
        obj = Organization(**validated_data, owner=self.context['request'].user)
        obj.save()
        obj.members.add(obj.owner)
        obj.save()
        # create a default collection for the group
        collection = Collection.objects.create(name=f'{obj.name}\'s collection', owner_id=obj.id, deletable=False)
        collection.save()
        return obj

    class Meta:
        model = Organization
        fields = ['id', 'name', 'group_visibility', 'owner']

# classes below are used to serialize the Group Members
class GroupInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['invite_token']

class GroupMemberIDSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApolloUser
        fields = ['id']