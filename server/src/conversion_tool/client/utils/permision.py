from rest_framework import permissions
from rest_framework_jwt.utils import jwt_decode_handler
from client.models import *

class AdminPermission(permissions.BasePermission):
    """
    Global permission for admin only.
    """

    def has_permission(self, request, view):
        decoded = jwt_decode_handler(request.META['HTTP_AUTHORIZATION'][4:])
        return int(decoded['role']) == 1


class ClientPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        decoded = jwt_decode_handler(request.META['HTTP_AUTHORIZATION'][4:])
        return int(decoded['role']) == 2
