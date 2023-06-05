from rest_framework import permissions

class IsAssignee(permissions.BasePermission):
    """
    Object-level permission to only allow assignee of a notification to see and read it.
    """

    def has_object_permission(self, request, view, obj):
        # Instance must have an attribute named `owner`.
        return obj.owner.members.contains(request.user)