from rest_framework import serializers
from django.http import HttpRequest
from django_countries.fields import CountryField
from .models import *
from client.models import Profile
from client.serializers import *
from django.core.exceptions import ValidationError


class CompanySerializer(serializers.ModelSerializer):
    podsRows = serializers.JSONField(write_only=True)
    adresRows = serializers.JSONField(write_only=True)
    address = serializers.CharField(allow_blank=True, required=False)
    zip_code = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = Company
        fields = ('id', 'name', 'func', 'surname', 'email', 'address', 'zip_code', 'podsRows',
                  'adresRows', 'cockpits', 'offers', 'crm_id', 'nom_entrepise', 'sex')
        read_only_fields = ('cockpits', 'offers')

    def create(self, validated_data):
        pods = validated_data['podsRows']
        validated_data.pop('podsRows')
        adds = validated_data['adresRows']
        validated_data.pop('adresRows')
        print 'validates', validated_data
        company = Company.objects.create(**validated_data)
        print company.id
        for index, obj in enumerate(pods):
            print obj['podsname'], adds[index]
            Meter.objects.create(meter_id=str(obj['podsname']), address=str(adds[index]['adresname']), company_id = company.id)
        return company

    def update(self, instance, validated_data):
        print validated_data
        pods = validated_data['podsRows']
        validated_data.pop('podsRows')
        adds = validated_data['adresRows']
        validated_data.pop('adresRows')

        instance.name = validated_data.get('name', instance.name)
        instance.email = validated_data.get('email', instance.email)
        instance.address = validated_data.get('address', instance.address)
        instance.zip_code = validated_data.get('zip_code', instance.zip_code)
        instance.func = validated_data.get('func', instance.func)
        instance.surname = validated_data.get('surname', instance.surname)
        instance.crm_id = validated_data.get('crm_id', instance.crm_id)
        instance.nom_entrepise = validated_data.get('nom_entrepise', instance.nom_entrepise)
        instance.sex = validated_data.get('sex', instance.sex)
        instance.save()

        # exists_pod = []
        # for pod in pods:
        #     try:
        #         exists_pod.append(pod['id'])
        #     except:
        #         print 'no pod'
        # meters = Meter.objects.filter(company = instance).values_list('id', flat=True)
        # for met in meters:
        #     try:
        #         if met not in exists_pod:
        #             meter = Meter.objects.get(id=int(met))
        #             meter.company = None
        #     except:
        #         print 'no pod'

        for index, obj in enumerate(pods):
            try:
                if obj['podsname'] != '':
                    print obj['id']
                    met, creat = Meter.objects.get_or_create(id=str(obj['id']))
                    met.meter_id = str(obj['podsname'])
                    met.address = str(adds[index]['adresname'])
                    met.company = instance
                    met.save()
            except:
                if obj['podsname'] != '':
                    met, creat = Meter.objects.get_or_create(meter_id=str(obj['podsname']), address=str(adds[index]['adresname']))
                    met.address = str(adds[index]['adresname'])
                    met.company = instance
                    met.save()
        return instance


class CompanyDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = ('id', 'name', 'company_id',)


class CompanyLogDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = ('id', 'name', 'surname', 'email', 'address', 'zip_code',
                  'crm_id', 'nom_entrepise', 'sex', 'last_log', 'last_offer', 'log_offer')


class SiteSerializer(serializers.ModelSerializer):
    company = CompanyDataSerializer()

    class Meta:
        model = Site
        fields = ('id', 'name', 'year', 'location', 'company', 'multisite', 'exists_offer')
        read_only_fields = ('id', 'exists_offer')


class SiteEditSerializer(serializers.ModelSerializer):
    meters = serializers.JSONField(read_only=True)
    sfile = serializers.CharField(read_only=True)
    # exists_offer = serializers.BooleanField(read_only=True)
    translation = serializers.IntegerField(read_only=True)
    year = serializers.IntegerField(read_only=True)

    class Meta:
        model = Site
        fields = ('id', 'name', 'year', 'meters', 'translation', 'location',
                  'company', 'multisite', 'sfile', 'exists_offer')
        read_only_fields = ('id', 'exists_offer')


class MeterSerializer(serializers.ModelSerializer):
    site = SiteSerializer()

    class Meta:
        model = Meter
        fields = ('id', 'meter_id', 'address', 'site', 'meter_sum')


class MeterEditSerializer(serializers.ModelSerializer):
    # site = serializers.IntegerField(required=False)

    class Meta:
        model = Meter
        fields = ('id', 'meter_id', 'address', 'site', 'meter_sum')


class CompanyLogSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Company
        fields = ('id', 'name', 'surname', 'nom_entrepise', 'email')


class CompanyExternSerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = ('emp_id', 'nom_entrepise', 'email')


class ClientLogSerializer(serializers.ModelSerializer):
    client = CompanyLogSerializer()
    admin = UserSerializer()
    offer_name = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = ClientLog
        fields = ('id', 'created', 'client', 'offer_name', 'offer_type', 'log_type', 'admin', 'device', 'last_offer')


class SmeEmailSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = SmeEmail
        fields = ('id', 'email',)
