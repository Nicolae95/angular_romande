from rest_framework import serializers
from companies.models import Meter, Site, Company
from django.http import HttpRequest
from django_countries.fields import CountryField
from django.contrib.auth.models import User

from .models import *
from core.models import *
from pfc.serializers import *
from companies.serializers import *

class BudgetCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = ('id', 'budget_id', 'pfc', 'pfc_market', 'cc', 'year')

    def create(self, validated_data):
        years = []
        for entry in EnergyConsumptionRecord.objects.filter(meter = validated_data['cc']).values_list('interval_start', flat=True):
            if entry.date().year not in years:
                years.append(entry.date().year)
        for year in years:
            validated_data['year'] = year
            budget = Budget.objects.create(**validated_data)
            budget.produce_report()
        return budget


class BudgetSerializer(serializers.ModelSerializer):
    pfc = PFCSerializer()
    pfc_market = PFCMarketSerializer()
    cc = MeterSerializer()

    class Meta:
        model = Budget
        fields = ('id', 'budget_id', 'site' , 'created', 'pfc', 'pfc_market', 'cc', 'budget_report', 'year')


class BudgetRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetRecord
        fields = ('id', 'value', 'unit', 'interval_start', 'budget', 'interval')


class BudgetSeasonRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetSeasonRecord
        fields = ('id', 'value', 'unit', 'interval_start', 'budget', 'interval', 'year', 'season', 'schedule')



# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ('id', 'value', 'unit', 'interval_start', 'budget', 'interval')
