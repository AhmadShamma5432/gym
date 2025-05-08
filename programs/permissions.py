from rest_framework import permissions

class IsCoachOrStaff(permissions.BasePermission):

    def has_permission(self, request, view):
        # Check if user is authenticated first
        if not request.user or not request.user.is_authenticated:
            return False

        user = request.user

        # Allow access if user is COACH, staff, or superuser
        return (
            user.role == 'COACH' or
            user.is_staff or
            user.is_superuser
        )