from rest_framework import serializers
from django.http import HttpRequest
from django_countries.fields import CountryField

from .models import *


class ProfileTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileType
        fields = ('id', 'name', 'year', 'data_file')
