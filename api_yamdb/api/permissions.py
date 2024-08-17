from rest_framework import permissions

from reviews.models import ADMIN, MODERATOR


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            if request.user.is_authenticated:
                if request.user.role == ADMIN:
                    return True
        return False


class IsAdminOrSuperuser(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return (
                request.user.role == ADMIN
                or request.user.is_superuser
                or request.user.is_admin
            )


class IsAuthorAdminModeratorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated or request.method in permissions.SAFE_METHODS:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        return (request.user.role == ADMIN or
                request.user.role == MODERATOR or
                request.user.is_superuser or
                request.user.is_admin or
                obj.author == request.user)
