from rest_framework import permissions


class RecruiterRequiredPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.user.is_recruiter or request.user.is_agency_recruiter:
                return True
        return False
