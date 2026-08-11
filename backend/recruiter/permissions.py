from rest_framework import permissions


class RecruiterRequiredPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user.is_authenticated
            and (request.user.is_recruiter or request.user.is_agency_recruiter)
        )
