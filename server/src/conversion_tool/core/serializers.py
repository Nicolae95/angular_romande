from rest_framework import serializers
from .models import EnergyConsumptionRecord, EnergyConsumptionReport, Shedule , Months, Weekday
from companies.models import Meter, Site, Company
from geo.models import Location
from django.http import HttpRequest
from django_countries.fields import CountryField




class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'name', 'country',)

    # def country_name(self, obj):
    #     request = self.context.get('request')
    #     country_name = obj.country.name
    #     return request.build_absolute_uri(country_name)

class MonthsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Months
        fields = ('id', 'name', 'month',)

class WeekdaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Weekday
        fields = ('id', 'name', 'day',)

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ('id', 'name',)

class SiteSerializer(serializers.ModelSerializer):
    company = CompanySerializer()
    location = LocationSerializer()
    class Meta:
        model = Site
        fields = ('name', 'location', 'company',)

class MeterSerializer(serializers.ModelSerializer):
    site = SiteSerializer()
    class Meta:
        model = Meter
        fields = ('meter_id', 'site',)

class RecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergyConsumptionRecord
        fields = ('from_file', 'meter', 'value', 'unit', 'interval_start', 'interval',)

# class SheduleSerializer(serializers.ModelSerializer):
#     months = MonthsSerializer(many=True)
#     weekdays = WeekdaySerializer(many=True)
#     weekend_days = WeekdaySerializer(many=True)
#
#     class Meta:
#         model = Shedule
#         fields = ('title', 'hours', 'months', 'weekdays', 'country', 'weekend_days', )

class SheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shedule
        fields = ('title',)

class ReportSerializer(serializers.ModelSerializer):
    result_file_url = serializers.SerializerMethodField()
    meter = MeterSerializer()
    shedules = SheduleSerializer(many=True)

    class Meta:
        model = EnergyConsumptionReport
        fields = ('title', 'meter', 'datetime_from', 'datetime_to', 'shedules', 'result_file_url',)

    def get_result_file_url(self, obj):
        request = self.context.get('request')
        if obj.result_file:
            result_file_url = obj.result_file.url
        else:
            result_file_url = '#'
        return request.build_absolute_uri(result_file_url)
