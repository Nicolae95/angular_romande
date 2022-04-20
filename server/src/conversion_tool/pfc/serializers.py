from rest_framework import serializers
from companies.models import Meter, Site, Company
from django.http import HttpRequest
from django_countries.fields import CountryField

from .models import *


class PfcConsumptionFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PfcConsumptionFile
        fields = ('id', 'pfc', 'pfc_market', 'data_file')
        readonly_fields = ('data_file',)


class PFCSerializer(serializers.ModelSerializer):
    class Meta:
        model = PFC
        fields = ('id', 'pfc_id', 'created',)


class PFCMarketSerializer(serializers.ModelSerializer):
    class Meta:
        model = PFCMarket
        fields = ('id', 'pfc_id', 'created',)
