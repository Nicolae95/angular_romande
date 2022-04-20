from __future__ import unicode_literals
from django.db import models
from django.apps import apps
from datetime import datetime, timedelta
from offers.models import *
from django_countries.fields import CountryField


class Company(models.Model):
    SEX_CHOICES = (
        ('F', 'Madame'),
        ('M', 'Monsieur'),
    )
    name = models.CharField(max_length=255)
    company_id = models.IntegerField(blank=True, null=True)
    crm_id = models.CharField(blank=True, max_length=255)
    nom_entrepise = models.CharField(blank=True, max_length=255)
    address = models.CharField(blank=True, null=True, max_length=255)
    zip_code = models.CharField(blank=True,  null=True, max_length=100)
    nick = models.CharField(blank=True, max_length=100)
    surname = models.CharField(blank=True, max_length=100)
    func = models.CharField(blank=True, max_length=100)
    email = models.EmailField(blank=True)
    phone = models.IntegerField(blank=True, null=True)
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, null=True, blank=True)

    def __unicode__(self):
        return self.name

    @property
    def emp_id(self):
        return self.id

    @property
    def cockpits(self):
        site = apps.get_model("companies", "Site")
        meter = apps.get_model("companies", "Meter")
        msite = site.objects.filter(company=self.id).values_list('id' , flat=True)
        mmeter = meter.objects.filter(site__in=msite, meter_sum=True).values_list('id' , flat=True)
        return Offer.objects.filter(cc__in=mmeter, cockpit=True, offer_status='indicative').values_list('name' , flat=True)

    @property
    def offers(self):
        site = apps.get_model("companies", "Site")
        meter = apps.get_model("companies", "Meter")
        msite = site.objects.filter(company=self.id).values_list('id' , flat=True)
        mmeter = meter.objects.filter(site__in=msite, meter_sum=True).values_list('id' , flat=True)
        return Offer.objects.filter(cc__in=mmeter, cockpit=False).values_list('name' , flat=True)
    
    @property
    def last_log(self):
        ClientLog = apps.get_model("companies", "ClientLog")
        try:
            l_log = ClientLog.objects.filter(client_id=self.id).order_by('-created')[0]
            return l_log.created
        except:
            return None
    
    @property
    def last_offer(self):
        Offer = apps.get_model("offers", "Offer")
        try:
            of = Offer.objects.filter(company_id=self.id).order_by('-created')[0]
            return of.id
        except:
            return None

    @property
    def log_offer(self):
        ClientLog = apps.get_model("companies", "ClientLog")
        try:
            l_log = ClientLog.objects.filter(client_id=self.id).order_by('-created')[0]
            return l_log.offer.name
        except:
            return None
    
    # @property
    # def podsRows(self):
    #     return 'podsRows'
    #
    # @property
    # def adresRows(self):
    #     return 'adresRows'




class Site(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    location = models.ForeignKey('geo.Location', null=True, blank=True)
    company = models.ForeignKey(Company)
    multisite = models.BooleanField(default=False)
    created = models.DateTimeField(default=datetime.now, blank=True)
    year = models.IntegerField(blank=True, null=True)
    format_donnees = models.DurationField(blank=True, null=True)

    @property
    def meters(self):
        return Meter.objects.filter(site_id=self.id, meter_sum=False).values('meter_id', 'address')

    @property
    def sfile(self):
        efile = apps.get_model('core', 'EnergyConsumptionFile')
        return efile.objects.get(site=self).data_file.name
    
    @property
    def exists_offer(self):
        Offer = apps.get_model('offers', 'Offer')
        meter = Meter.objects.get(site_id=self.id, meter_sum=True)
        suprimer = Offer.objects.filter(cc=meter, offer_status='supprimer')
        offs = Offer.objects.filter(cc=meter)
        if (len(suprimer) == len(offs)):
            return False
        else:
            return Offer.objects.filter(cc=meter).exists()

    @property
    def translation(self):
        return Meter.objects.get(site_id=self.id, meter_sum=True).id

    def __unicode__(self):
        return '{} from {}'.format(self.name or str(self.id), self.company)

    class Meta:
        ordering = ('-pk',)


class Meter(models.Model):
    # meter_id = models.CharField(max_length=255, unique=True)
    meter_id = models.CharField(max_length=255)
    site = models.ForeignKey(Site, on_delete=models.SET_NULL, null=True, blank=True)
    company = models.ForeignKey(Company, null=True, blank=True)
    meter_sum = models.BooleanField(default=False)
    address = models.CharField(max_length=255, blank=True)

    def __unicode__(self):
        return '{} : {}'.format(self.meter_id, self.site)

    class Meta:
        ordering = ('-pk',)


class ClientLog(models.Model):
    LOG_CHOICES = (
        ('open', 'Open Offer Email'),
        ('click', 'Click Offer Email'),
        ('send', 'Offer Send Email'),
        ('signer', 'Click Offer signer'),
        ('signee', 'Click Offer signee'),
        ('created', 'Createe Offer'),
        ('confirmer', 'Confirmer Offer'),
        ('aconfirmer', 'A Confirmer Offer'),
        ('refuse', 'Refuse Offer'),
    )

    DEVICE_CHOICES = (
        ('mobile', 'Mobile'),
        ('desktop', 'Desktop'),
    )
    created = models.DateTimeField(default=datetime.now, blank=True)
    country = CountryField(null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    client = models.ForeignKey(Company)
    offer = models.ForeignKey('offers.Offer', null=True, blank=True)
    log_type = models.CharField(max_length=100, choices=LOG_CHOICES, null=True, blank=True)
    device = models.CharField(max_length=100, choices=DEVICE_CHOICES, default='desktop', null=True, blank=True)
    ip = models.CharField(max_length=255, null=True, blank=True)
    admin = models.ForeignKey(User, null=True, blank=True, related_name='log_client_admin')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    @property
    def offer_name(self):
        return self.offer.name
    
    @property
    def admin_name(self):
        return self.offer.name
    
    @property
    def offer_type(self):
        return self.offer.offer_type
    
    @property
    def last_offer(self):
        Offer = apps.get_model("offers", "Offer")
        try:
            of = Offer.objects.filter(company=self.client).order_by('-created')[0]
            return of.id
        except:
            return None
    

class SmeEmail(models.Model):
    email = models.EmailField(blank=True)

    def __unicode__(self):
        return self.email
