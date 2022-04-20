from rest_framework import serializers
from companies.models import Meter, Site, Company
from django.http import HttpRequest
from django_countries.fields import CountryField

from .models import *
from companies.serializers import *

class TranslationEditSerializer(serializers.ModelSerializer):

    class Meta:
        model = Translation
        fields = ('cc', 'years')

    # def create(self, validated_data):
    #     obj = Translation.objects.create(**validated_data)
    #     # obj.process_data()
    #     return obj


class TranslationSerializer(serializers.ModelSerializer):
    cc = MeterSerializer()

    class Meta:
        model = Translation
        fields = ('id', 'created', 'cc', 'years')
