from rest_framework import serializers
from django.http import HttpRequest
from django_countries.fields import CountryField
from datetime import datetime, timedelta, time
import pytz
from .models import *
from companies.serializers import *
from offers.serializers import *


class DateTimeFieldCET(serializers.DateTimeField):
    '''Class to make output of a DateTime Field timezone aware
    '''

    def to_representation(self, value):
        cet = pytz.timezone('UTC')
        # value = cet.localize(value)
        interval_cc = pytz.utc.localize(datetime.strptime(str(value)[:16], '%Y-%m-%d %H:%M'))
        value = interval_cc.astimezone(pytz.timezone('CET'))
        expiration_date = value.strftime('%d/%m/%Y %H:%M')
        # return super(DateTimeFieldUTC, self).to_representation(str(value))
        return super(DateTimeFieldCET, self).to_representation(expiration_date)


class CockpitNewsSerializer(serializers.ModelSerializer):

    class Meta:
        model = CockpitNews
        fields = ('id', 'name', 'clients')


class CockpitOfferNewsSerializer(serializers.ModelSerializer):

    class Meta:
        model = CockpitNews
        fields = ('id', 'offers')


class CockpitNewsDataSerializer(serializers.ModelSerializer):
    clients = CompanyLogSerializer(many=True)
    offers = OfferSerializer(many=True)
    created = DateTimeFieldCET()

    class Meta:
        model = CockpitNews
        fields = ('id', 'name', 'email_name', 'clients',
                  'offers', 'created', 'emp_news', 'romande_news', 'automatic', 'weekdays', 'month')


class CockpitNewsEditSerializer(serializers.ModelSerializer):

    class Meta:
        model = CockpitNews
        fields = ('id', 'name', 'emp_news', 'romande_news', 'email_name', 'automatic', 'weekdays', 'month')


class NewsCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = NewsCategory
        fields = ('id', 'name',)


class NewsSerializer(serializers.ModelSerializer):

    class Meta:
        model = News
        fields = ('id', 'category', 'cockpit', 'text')


class CockpitMarketSerializer(serializers.ModelSerializer):

    class Meta:
        model = CockpitMarket
        fields = ('id', 'name', 'category', 'market_id', 'currency', 'description', 'unit')


class ChartSerializer(serializers.ModelSerializer):

    class Meta:
        model = Chart
        fields = ('id', 'name', 'cockpit', 'markets', 'tabel', 'chart')


class ChartCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Chart
        fields = ('id', 'name', 'cockpit', 'markets', 'tabel', 'chart')


class ChartEditMarketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Chart
        fields = ('id', 'markets')


class ChartAddMarketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Chart
        fields = ('id', 'markets')

    def update(self, instance, validated_data):
        instance.markets.add(*validated_data['markets'])
        instance.save()
        return instance


class ChartMarketSerializer(serializers.ModelSerializer):
    markets = CockpitMarketSerializer(many=True)

    class Meta:
        model = Chart
        fields = ('id', 'name', 'cockpit',  'markets', 'tabel', 'chart')


class CockpitSerializer(serializers.ModelSerializer):
    weekdays = serializers.JSONField(read_only=True)

    class Meta:
        model = Cockpit
        fields = ('id', 'name', 'weekday', 'weekdays')


class CockpitEditSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cockpit
        fields = ('id', 'name')


class CockpitOfferSerializer(serializers.ModelSerializer):
    cockpit = CockpitEditSerializer()

    class Meta:
        model = CockpitOffer
        fields = ('id', 'weekday', 'cockpit', 'offer', 'highest',
                  'lowest', 'date_from', 'date_to', 'email', 'year')


class CockpitFirstOfferSerializer(serializers.ModelSerializer):
    date_from = serializers.DateTimeField(format="%Y-%m-%d", required=False)
    date_to = serializers.DateTimeField(format="%Y-%m-%d", required=False)
    email = serializers.EmailField(allow_blank=True)

    class Meta:
        model = CockpitOffer
        fields = ('highest', 'lowest', 'date_from', 'date_to', 'email', 'year')
