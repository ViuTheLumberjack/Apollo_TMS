from rest_framework import permissions
from .models import Assignment

class IsGroupMember(permissions.BasePermission):
    """
    Object-level permission to only allow members of a group that owns the collection to view it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Instance must have an attribute named `owner`.
        return obj.owner.members.contains(request.user)
    
class CanBeSeen(permissions.BasePermission):
    """
    Object-level permission to only allow members of a group that owns the collection to view it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Instance must have an attribute named `owner`.
        return obj.collection.members.contains(request.user)
    
class IsGroupOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return obj.owner.owner == request.user
    
class IsAssignee(permissions.BasePermission):
    """
    Object-level permission to only allow people assign to a task to modify status.
    """

    def has_object_permission(self, request, view, obj):
        # Instance must have an attribute named `owner`.
        try:
            assignment = Assignment.objects.get(user=request.user, task=obj)
            return True
        except Assignment.DoesNotExist:
            return False 