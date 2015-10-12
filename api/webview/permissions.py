from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of pushed data to edit it
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to view any request, always allow
        # GET, HEAD or OPTIONS requests

        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the source of the data
        return obj.source == request.user
