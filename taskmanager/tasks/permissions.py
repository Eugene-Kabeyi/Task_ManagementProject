from rest_framework import permissions

class IsTaskOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a task to access it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Check if the task belongs to the requesting user
        return obj.user == request.user

class IsCategoryOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a category to access it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Check if the category belongs to the requesting user
        return obj.user == request.user