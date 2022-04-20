from rest_framework import permissions
from rest_framework_jwt.utils import jwt_decode_handler
from client.models import *


def user_permission(user_id, request):
        decoded = jwt_decode_handler(request.META['HTTP_AUTHORIZATION'][4:])
        return int(decoded['user_id']) == user_id
