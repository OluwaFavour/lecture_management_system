from rest_framework.permissions import BasePermission

from .authentication_classes import SessionAuthentication


class IsLecturer(BasePermission):
    def has_permission(self, request, view):
        auth_result = SessionAuthentication().authenticate(request)
        if auth_result is not None:
            user, _ = auth_result
        else:
            user = None
        return user.is_lecturer if user else False


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        auth_result = SessionAuthentication().authenticate(request)
        if auth_result is not None:
            user, _ = auth_result
        else:
            user = None
        return not user.is_lecturer if user else False


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        auth_result = SessionAuthentication().authenticate(request)
        if auth_result is not None:
            user, _ = auth_result
        else:
            user = None
        return user.is_superuser or user.is_staff if user else False


class IsClassRep(BasePermission):
    def has_permission(self, request, view):
        auth_result = SessionAuthentication().authenticate(request)
        if auth_result is not None:
            user, _ = auth_result
        else:
            user = None
        return user.is_class_rep if user else False


class IsRegistrationOfficer(BasePermission):
    def has_permission(self, request, view):
        auth_result = SessionAuthentication().authenticate(request)
        if auth_result is not None:
            user, _ = auth_result
        else:
            user = None
        return user.is_registration_officer if user else False
