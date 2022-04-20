from rest_framework import serializers
from django.http import HttpRequest
from django_countries.fields import CountryField

from .models import *


class ProfileTypePondereSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileTypePondere
        fields = ('id', 'name', 'year', 'data_file')
