# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.apps import apps
from django.db import models
from companies.models import *
from core.models import *
import uuid
from utils.upload_grd import upload
from django.db.models import F



class OfferStop(models.Model):
    stop = models.BooleanField(default=False)

    class Meta:
        ordering = ('-pk',)

    def __unicode__(self):
        return '{}'.format(self.stop)



class GRDFile(TimeStampedModel):
    data_file = models.FileField()

    def __unicode__(self):
        return self.data_file.name

    def save(self, *args, **kwargs):
        if not self.pk:
            super(GRDFile, self).save(*args, **kwargs)
            self.process_file()
        super(GRDFile, self).save(*args, **kwargs)

    @transaction.atomic
    def process_file(self):
        cet = pytz.timezone('UTC')
        parse = False
        print self.data_file.file
        fileName, fileExtension = os.path.splitext(self.data_file.file.name)
        print fileName, fileExtension
        if fileExtension.lower() == '.xlsx' or fileExtension.lower() == '.xls':
            upload(self, self.data_file.file)
        else:
            'error'


class GRD(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    ligne1 = models.CharField(max_length=255, blank=True, null=True)
    ligne2 = models.CharField(max_length=255, blank=True, null=True)
    ligne3 = models.CharField(max_length=255, blank=True, null=True)
    ligne4 = models.CharField(max_length=255, blank=True, null=True)
    ligne5 = models.CharField(max_length=255, blank=True, null=True)
    ligne6 = models.CharField(max_length=255, blank=True, null=True)
    ligne7 = models.CharField(max_length=255, blank=True, null=True)
    ligne8 = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ('-pk',)

    def __unicode__(self):
        return '{}'.format(self.name)

    @property
    def int_ligne8(self):
        return str(int(self.ligne8))




class Constants(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    value = models.FloatField(blank=True, null=True)

    class Meta:
        ordering = ('-pk',)

    def __unicode__(self):
        return '{} - {}'.format(self.name, self.value)



class Risc(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(null=True, blank=True, max_length=255)
    default = models.BooleanField(default=False)

    class Meta:
        ordering = ('-name',)

    def __unicode__(self):
        return self.name


class RiscRecord(models.Model):
    risc = models.ForeignKey(Risc, null=True, related_name='risc')
    pfc = models.ForeignKey('pfc.PFC', null=True, related_name='risc_pfc')
    pfc_market = models.ForeignKey('pfc.PFCMarket', null=True, related_name='risc_pfc_market')
    value = models.FloatField()
    unit = models.CharField(max_length=255, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    file = models.CharField(max_length=255, null=True, blank=True)
    rid = models.CharField(max_length=255, blank=True, null=True)


    class Meta:
        ordering = ('-pk',)

    def __unicode__(self):
        return '{} from year {}'.format(self.value, self.year)


class Offer(models.Model):

    to_10 = 'to_10'
    to_50 = 'to_50'
    to_100 = 'to_100'
    more_than_100 = 'more_than_100'
    EMPLOOYEES_CHOICES = (
        (to_10, 'From 1 to 10'),
        (to_50, 'From 11 to 50'),
        (to_100, 'From 51 to 100'),
        (more_than_100, 'More than 100'),
    )

    standart = 'Standart'
    sme = 'SME'
    TYPE_CHOICES = (
        (standart, 'Standard'),
        (sme, 'SME'),
    )

    SECOND_TYPE_CHOICES = (
        ('prolongation', 'Prolongation'),
        ('acquisition', 'Acquisition'),
        ('retention', 'Retention'),
    )

    STATUS_CHOICES = (
        ('pending', 'En cours'),
        ('confirmer', 'A Confirmer'),
        ('ferme', 'Ferme'),
        ('indicative', 'Prix indicatifs'),
        ('signer', 'Offre A signer'),
        ('signee', 'Offre signee'),
        ('supprimer', 'A supprimer'),
    )

    ENERGY_CHOICES = (
        ('energy1', 'Certificats hydrauliques suisses naturemade star'),
        ('energy2', 'Certificats hydrauliques suisses'),
        ('energy3', 'Certificats nucléaires suisses '),
        ('energy4', 'Certificats mix hydrauliques-solaires suisses'),
        ('energy5', 'Certificats hydrauliques romands naturemade star'),
        ('energy6', 'Certificats hydrauliques européens'),
        ('energy7', 'Certificats hydro suisse naturemade basic'),
        ('energy8', 'Certificats solaire suisse naturemade star'),
        ('energy9', 'Certificats custom'),
    )

    FUNC_CHOICES = (
        (1, 'Account Manager'),
        (2, 'Key Account Manager'),
        (3, 'Responsable du service Tarification et Pricing'),
        (4, 'Responsable Marchés'),
        (5, 'Directeur REC SA'),
        (6, 'Responsable du Groupe Account Manager'),
        (7, 'Responsable Qualité Ressource Energie'),
        (8, 'Responsable du Marché Entreprises et Collectivités Analyste Pricing'),
        (9, 'CEO'),
    )

    unique_id = models.UUIDField(default=uuid.uuid4, unique=True)
    emp_id = models.IntegerField(blank=True, null=True)
    # opportunite = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    company = models.ForeignKey('companies.Company', null=True, blank=True)
    consumption = models.FloatField(null=True, blank=True)
    created = models.DateTimeField(default=datetime.now, blank=True)
    updated = models.DateTimeField(default=datetime.now, blank=True)
    signee_date = models.DateTimeField(null=True, blank=True)
    # weekdays = models.ManyToManyField('core.Weekday', blank=True, related_name='offer_weekdays')
    datetime_from = models.DateTimeField(null=True, blank=True)
    datetime_to = models.DateTimeField(null=True, blank=True)
    employees = models.CharField(choices=EMPLOOYEES_CHOICES, max_length=255, null=True, blank=True)
    pfc = models.ForeignKey('pfc.PFC', null=True, blank=True, related_name='offer_pfc')
    pfc_market = models.ForeignKey('pfc.PFCMarket', null=True, blank=True, related_name='offer_market')
    profile = models.ForeignKey('type.ProfileType', null=True, blank=True, related_name='offer_profile')
    profile_pondere = models.ForeignKey('typepondere.ProfileTypePondere', null=True, blank=True, related_name='offer_pondere')
    cc = models.ForeignKey('companies.Meter', null=True, blank=True, related_name='offer_cc')
    grd = models.ForeignKey(GRD, null=True, blank=True, related_name='offer_grd')
    years = models.CharField(blank=True, max_length=255)
    lis_years = models.CharField(blank=True, max_length=255)
    unit = models.CharField(blank=True, max_length=255)
    offer_type = models.CharField(choices=TYPE_CHOICES, max_length=255, null=True, blank=True)
    second_type = models.CharField(choices=SECOND_TYPE_CHOICES, max_length=255, null=True, blank=True)
    energy_type = models.CharField(choices=ENERGY_CHOICES, max_length=255, null=True, blank=True)
    riscs = models.ManyToManyField(Risc, blank=True, related_name='offer_riscs')
    shedules = models.ManyToManyField('core.Shedule', blank=True, related_name='offer_shedules')
    validation_time = models.IntegerField(blank=True, null=True)
    expiration_date = models.DateTimeField(null=True, blank=True)
    date_debut = models.DateTimeField(null=True, blank=True)
    date_fin = models.DateTimeField(null=True, blank=True)
    mail_date = models.DateTimeField(null=True, blank=True)
    offer_status = models.CharField(choices=STATUS_CHOICES, default="indicative", max_length=255, null=True, blank=True)
    sme_status = models.CharField(choices=STATUS_CHOICES, default="indicative", max_length=255, null=True, blank=True)
    cockpit = models.BooleanField(default=False)
    lissage = models.BooleanField(default=False)
    lissage_years = models.TextField(blank=True)
    user = models.ForeignKey(User, null=True, blank=True, related_name='offer_user_id')
    conseiller = models.ForeignKey(User, null=True, blank=True, related_name='offer_conseiller_id')
    signer = models.ForeignKey(User, null=True, blank=True, related_name='offer_signer')
    signed_file = models.FileField(upload_to='signed/', null=True, blank=True)
    unsigned_file = models.FileField(upload_to='unsigned/', null=True, blank=True)
    eligibilite = models.FileField(upload_to='eligibilite/', null=True, blank=True)
    marche = models.BooleanField(default=False)
    releve = models.BooleanField(default=False)
    token = models.UUIDField(null=True, blank=True)
    comment = models.TextField(blank=True)
    emails = models.TextField(blank=True)
    nr_opportunite = models.CharField(blank=True, max_length=255)
    volumetrie = models.FloatField(null=True, blank=True)
    marge = models.FloatField(null=True, blank=True)
    signatures = models.ManyToManyField(User, blank=True)
    fonction = models.PositiveSmallIntegerField(choices=FUNC_CHOICES, default=3, null=True, blank=True)
    percent = models.IntegerField(null=True, blank=True)
    lis_force = models.BooleanField(default=False)
    lis_manual_expire = models.DateTimeField(null=True, blank=True)
    lissage_base = models.IntegerField(null=True, blank=True)
    status_lisse = models.BooleanField(default=False)
    risc = models.CharField(max_length=255, null=True, blank=True)
    eco = models.CharField(max_length=255, null=True, blank=True)
    pfc_date_first = models.DateTimeField(null=True, blank=True)
    pfc_date_last = models.DateTimeField(null=True, blank=True)



    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('-pk',)

    # def save(self, *args, **kwargs):
    #     if not self.emp_id:
    #         self.emp_id = self.id + 10000
    #     super(Offer, self).save(*args, **kwargs)

    @property
    def otype(self):
        if self.offer_type == 'Standart':
            return 'STD'
        elif self.offer_type == 'SME':
            return 'SME'
    
    @property
    def hp_hc(self):
        if len(self.shedules.all()) == 1:
            return 'Unique'
        else:
            return 'HP_HC'
    
    @property
    def duree(self):
        if self.date_fin and self.date_debut:
            return round((self.date_fin - self.date_debut).total_seconds())
        else:
            return 0
    
    @property
    def name_unsigned(self):
        if self.unsigned_file:
            return str(self.unsigned_file)
        else:
            return ''
    
    @property
    def name_signed(self):
        if self.signed_file:
            return str(self.signed_file)
        else:
            return ''
    
    @property
    def name_eligib(self):
        if self.eligibilite:
            return str(self.eligibilite)
        else:
            return ''

    @property
    def entreprise(self):
        return self.company.nom_entrepise
    
    @property
    def contact(self):
        return self.company.name
    
    @property
    def surname(self):
        return self.company.surname
    
    @property
    def id_lissee(self):
        return self.lissage_base
    
    @property
    def localite(self):
        try:
            return self.company.zip_code.split(' ')[1]
        except:
            return ''

    @property
    def energyd(self):
        """Returns the display value given the db value"""
        for (db_val, display_val) in self.ENERGY_CHOICES:
            if db_val == self.energy_type and self.energy_type != 'energy9':
                return display_val
            if db_val == self.energy_type and self.energy_type == 'energy9':
                if self.pfc_market:
                    return self.pfc_market.custom
                else:
                    ''
        return ''
    
    @property
    def offer_function(self):
        """Returns the display value given the db value"""
        for (db_val, display_val) in self.FUNC_CHOICES:
            if db_val == self.fonction:
                return display_val
        return ''

    @property
    def meters(self):
        meter = apps.get_model("companies", "Meter")
        if self.cc.site_id:
            return meter.objects.filter(site_id=self.cc.site_id, meter_sum=False).values('meter_id', 'address')
        else:
            return []

    @property
    def address_pods(self):
        meter = apps.get_model("companies", "Meter")
        if self.cc.site_id:
            return meter.objects.filter(site_id=self.cc.site_id, meter_sum=False).values('meter_id', 'address')
        else:
            return []

    @property
    def type(self):
        """Returns the display value given the db value"""
        for (db_val, display_val) in self.TYPE_CHOICES:
            if db_val == self.offer_type:
                return display_val
        return ''
    
    @property
    def status(self):
        """Returns the display value given the db value"""
        for (db_val, display_val) in self.STATUS_CHOICES:
            if db_val == self.offer_status and self.status_lisse == False:
                return display_val
            if self.offer_status == 'signee' and self.status_lisse == True:
                return 'LISSEE'
        return ''

    @property
    def years_signee(self):
        if self.offer_status == 'signee':
            return self.years.split(',')
        else:
            return []

    @property
    def prix_resa_rec(self):
        BudgetAveragePerYear = apps.get_model("budget", "BudgetAveragePerYear")
        Budget = apps.get_model("budget", "Budget")
        if self.offer_type == 'SME':
            prices = BudgetAveragePerYear.objects.filter(budget_id__in=Budget.objects.filter(
                offer_id=self.id, pfc_market=self.pfc_market).values_list('id', flat=True)).values('year', 'value')
        else:
            prices = BudgetAveragePerYear.objects.filter(budget_id__in=Budget.objects.filter(
                offer_id=self.id, pfc=self.pfc).values_list('id', flat=True)).values('year', 'value')
        return prices

    
    @property
    def prix_vente_hors_go_produitservice(self):
        BudgetAverageMajorationPerYear = apps.get_model("budget", "BudgetAverageMajorationPerYear")
        Budget = apps.get_model("budget", "Budget")
        if self.offer_type == 'SME':
            prices = BudgetAverageMajorationPerYear.objects.filter(budget_id__in=Budget.objects.filter(
                offer_id=self.id, pfc_market=self.pfc_market).values_list('id', flat=True)).values('year', 'value')
        else:
            prices = BudgetAverageMajorationPerYear.objects.filter(budget_id__in=Budget.objects.filter(
                offer_id=self.id, pfc=self.pfc).values_list('id', flat=True)).values('year', 'value')
        return prices


    @property
    def prix_vente_final(self):
        BudgetAveragePerYearRiscs = apps.get_model("budget", "BudgetAveragePerYearRiscs")
        Budget = apps.get_model("budget", "Budget")
        if self.offer_type == 'SME':
            prices = BudgetAveragePerYearRiscs.objects.filter(budget_id__in=Budget.objects.filter(
                offer_id=self.id, pfc_market=self.pfc_market).values_list('id', flat=True)).values('year', 'value')
        else:
            prices = BudgetAveragePerYearRiscs.objects.filter(budget_id__in=Budget.objects.filter(
                offer_id=self.id, pfc=self.pfc).values_list('id', flat=True)).values('year', 'value')
        return prices


    @property
    def prix_resa_rec_hp_hc(self):
        BudgetMedSeasonRecord = apps.get_model("budget", "BudgetMedSeasonRecord")
        Budget = apps.get_model("budget", "Budget")
        if self.offer_type == 'SME':
            prices = BudgetMedSeasonRecord.objects.filter(budget_id__in=Budget.objects.filter(
                offer_id=self.id, pfc_market=self.pfc_market).values_list('id', flat=True)).annotate(hp_hc=F('schedule__title')).values('year', 'value', 'hp_hc', 'season')
        else:
            prices = BudgetMedSeasonRecord.objects.filter(budget_id__in=Budget.objects.filter(
                offer_id=self.id, pfc=self.pfc).values_list('id', flat=True)).annotate(hp_hc=F('schedule__title')).values('year', 'value', 'hp_hc', 'season')
        
        for d in prices:
            d.update((k, "HC") for k, v in d.iteritems() if v == "OffPeak")
        for d in prices:
            d.update((k, "HP") for k, v in d.iteritems() if v == "Peak")
        
        for d in prices:
            d.update((k, "ÉTÉ") for k, v in d.iteritems() if v == "Summer")
        for d in prices:
            d.update((k, "HIVER") for k, v in d.iteritems() if v == "Winter")
        
        return prices


    @property
    def prix_vente_hors_go_produitservice_hp_hc(self):
        BudgetMedSeasonMajorationRecord = apps.get_model("budget", "BudgetMedSeasonMajorationRecord")
        Budget = apps.get_model("budget", "Budget")
        if self.offer_type == 'SME':
            prices = BudgetMedSeasonMajorationRecord.objects.filter(budget_id__in=Budget.objects.filter(
                offer_id=self.id, pfc_market=self.pfc_market).values_list('id', flat=True)).annotate(hp_hc=F('schedule__title')).values('year', 'value', 'hp_hc', 'season')
        else:
            prices = BudgetMedSeasonMajorationRecord.objects.filter(budget_id__in=Budget.objects.filter(
                offer_id=self.id, pfc=self.pfc).values_list('id', flat=True)).annotate(hp_hc=F('schedule__title')).values('year', 'value', 'hp_hc', 'season')
        for d in prices:
            d.update((k, "HC") for k, v in d.iteritems() if v == "OffPeak")
        for d in prices:
            d.update((k, "HP") for k, v in d.iteritems() if v == "Peak")
        
        for d in prices:
            d.update((k, "ÉTÉ") for k, v in d.iteritems() if v == "Summer")
        for d in prices:
            d.update((k, "HIVER") for k, v in d.iteritems() if v == "Winter")

        return prices

    @property
    def prix_vente_final_hp_hc(self):
        BudgetMedSeasonWithRiscsRecord = apps.get_model("budget", "BudgetMedSeasonWithRiscsRecord")
        Budget = apps.get_model("budget", "Budget")
        if self.offer_type == 'SME':
            prices = BudgetMedSeasonWithRiscsRecord.objects.filter(budget_id__in=Budget.objects.filter(
                offer_id=self.id, pfc_market=self.pfc_market).values_list('id', flat=True)).annotate(hp_hc=F('schedule__title')).values('year', 'value', 'hp_hc', 'season')
        else:
            prices = BudgetMedSeasonWithRiscsRecord.objects.filter(budget_id__in=Budget.objects.filter(
                offer_id=self.id, pfc=self.pfc).values_list('id', flat=True)).annotate(hp_hc=F('schedule__title')).values('year', 'value', 'hp_hc', 'season')
        for d in prices:
            d.update((k, "HC") for k, v in d.iteritems() if v == "OffPeak")
        for d in prices:
            d.update((k, "HP") for k, v in d.iteritems() if v == "Peak")
        
        for d in prices:
            d.update((k, "ÉTÉ") for k, v in d.iteritems() if v == "Summer")
        for d in prices:
            d.update((k, "HIVER") for k, v in d.iteritems() if v == "Winter")

        return prices


    @property
    def ID_PFC_ajustee(self):
        return self.pfc.file

    @property
    def ID_primes_risques(self):
        return self.pfc.risc

    @property
    def ID_garanties_origine(self):
        return self.pfc.eco


    @property
    def years_list(self):
        return sorted(self.years.split(','))

    @property
    def years_liss_list(self):
        return sorted(self.lis_years.split(','))
    
    @property
    def emails_list(self):
        return self.emails.split(',')

    @property
    def decotes(self):
        return str(ParameterRecord.objects.filter(year__in=map(lambda y: int(y), self.years.split(',')),
                                                  parameter = Parameter.objects.get(code='decode'),
                                                  offer_id = self.id).values_list('value', flat=True))

    @property
    def efforts(self):
        return str(ParameterRecord.objects.filter(year__in=map(lambda y: int(y), self.years.split(',')),
                                                  parameter = Parameter.objects.get(code='efforts'),
                                                  offer_id = self.id).values_list('value', flat=True))

    @property
    def energies(self):
        return str(ParameterRecord.objects.filter(year__in=map(lambda y: int(y), self.years.split(',')),
                                                  parameter = Parameter.objects.get(code='energies'),
                                                  offer_id = self.id).values_list('value', flat=True))

    @property
    def majors(self):
        return str(ParameterRecord.objects.filter(year__in=map(lambda y: int(y), self.years.split(',')),
                                                  parameter = Parameter.objects.get(code='majors'),
                                                  offer_id = self.id).values_list('value', flat=True))

    @property
    def ps1(self):
        return str(ParameterRecord.objects.filter(year__in=map(lambda y: int(y), self.years.split(',')),
                                                  parameter = Parameter.objects.get(code='ps1'),
                                                  offer_id = self.id).values_list('value', flat=True))

    @property
    def ps2(self):
        return str(ParameterRecord.objects.filter(year__in=map(lambda y: int(y), self.years.split(',')),
                                                  parameter = Parameter.objects.get(code='ps2'),
                                                  offer_id = self.id).values_list('value', flat=True))

    @property
    def sur_go(self):
        return str(ParameterRecord.objects.filter(year__in=map(lambda y: int(y), self.years.split(',')),
                                                  parameter = Parameter.objects.get(code='ps2'),
                                                  offer_id = self.id).values_list('value', flat=True))
    
    @property
    def cockpit_data(self):
        CockpitOffer = apps.get_model("cockpit", "CockpitOffer")
        Cockpit = apps.get_model("cockpit", "Cockpit")
        if self.cockpit:
            try:
                cock = CockpitOffer.objects.filter(offer_id=self.id, cockpit_id=1).values_list('cockpit__name', flat=True)
                cockh = CockpitOffer.objects.filter(offer_id=self.id, cockpit_id=3).values_list('cockpit__name', flat=True)
                cocklist = CockpitOffer.objects.filter(offer_id=self.id, cockpit_id=2).values_list('weekday__name', flat=True)
                if cocklist:
                    return list(cocklist)
                if cockh:
                    return list(cockh)
                if cock:
                    return [cock[0]]
            except:
                return []
        else:
            return []


    @property
    def pfc_data(self):
        if self.offer_type == 'Standart':
            return {
                    'pfc_EMP_id': self.pfc.pfc_id, 
                    'pfc_id': self.pfc.file,
                    'primes de risque id': self.pfc.risc,
                    'eco-énergies id': self.pfc.eco
                    }
        elif self.offer_type == 'SME':
            return {}
    
    @property
    def admin_data(self):
        return {
            'emp_id': self.user.id,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
        }
    
    @property
    def grd_name(self):
        return self.grd.ligne1
        

    # def process_data(self):
    #     if self.cc:
    #         cc_data = EnergyConsumptionRecord.objects.filter()


class Parameter(models.Model):
    code = models.CharField(unique=True, max_length=255)
    name = models.CharField(max_length=255)
    final = models.BooleanField(default=False)


    class Meta:
        ordering = ('-name',)

    def __unicode__(self):
        return self.name


class ParameterRecord(models.Model):
    parameter = models.ForeignKey(Parameter, null=True, related_name='parameter')
    offer = models.ForeignKey(Offer, null=True, related_name='parameter_offer')
    value = models.FloatField()
    unit = models.CharField(max_length=255, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ('-pk',)

    def __unicode__(self):
        return '{} from year {}'.format(self.value, self.year)


class OfferPlot(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE)
    figure = models.ImageField(upload_to='plots/')
    created = models.DateTimeField(default=datetime.now, blank=True)

    def __unicode__(self):
        return str(self.pk)

    class Meta:
        ordering = ('-pk',)


@receiver(post_save, sender=Offer)
def my_handler(sender, instance, **kwargs):
    if not instance.emp_id:
        instance.emp_id = instance.id + 10000
        instance.save()
