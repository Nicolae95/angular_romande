# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import *
from django.contrib.auth.models import User
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from datetime import datetime, timedelta
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core import serializers
from django.utils.timezone import get_current_timezone, make_aware, make_naive
from django.utils import timezone
from django.conf import settings
from pytz import country_timezones
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpRequest
from rest_framework.pagination import LimitOffsetPagination
from django.core.files import File
import json
import ast
import pytz
import os
import uuid
import base64
from django.views.generic import View
from rest_framework import viewsets
from collections import defaultdict
from operator import itemgetter
from rest_framework import status
from django.db.models import Sum
from utils.send_mail import py_mail
from .models import *
from companies.models import *
from pfc.models import *
from client.models import *
from cockpit.models import *
from .serializers import *
from cockpit.serializers import *
from django.contrib.gis.geoip2 import GeoIP2
from pfc.logic.cockpit.check import new_data, update_data, update_market_data, get_last_pfc


def expiration_date(validation_time):
        date = datetime.utcnow()
        # if int(validated_data['validation_time']) == 1:
        #     expiration_date = datetime.utcnow() + timedelta(days=1)
        expiration_date = datetime.utcnow() + timedelta(days=int(validation_time))
        list_days = [date + timedelta(days=x) for x in range((expiration_date-date).days)]
        try:
            holidays = Location.objects.all()[0].holidays.all().values_list('date', flat=True)
            print holidays
        except:
            holidays = []
        weekend = 0
        for day in list_days:
            if day.isoweekday() > 5:
                weekend = weekend + 1
            else:
                if day in holidays:
                    weekend = weekend + 1
        
        print 'weekend =========== ', weekend
        if int(validation_time) > 0:
            exp = datetime.utcnow() + timedelta(days = int(validation_time)-1 + weekend)
        else:
            exp = datetime.utcnow() + timedelta(days = 0 + weekend)
        
        print 'exp ================ ', exp, 8-exp.isoweekday()

        if exp.isoweekday() > 5:
            return exp.replace(hour=23, minute=59) + timedelta(days=8-exp.isoweekday())
        else:
            return exp.replace(hour=23, minute=59)


class OfferAddEMPIdSet(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        offers = Offer.objects.all()
        for offer in offers:
            if not offer.emp_id:
                offer.emp_id = offer.id + 10000
                offer.updated = offer.created
                offer.save()
        return Response(status=status.HTTP_200_OK)


class OfferStopViewListSet(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)


    def get(self, request, format=None):
        snippets = OfferStop.objects.all()
        serializer = OfferStopSerializer(snippets, context={"request": request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def put(self, request, format=None):
        try:
            snippet = OfferStop.objects.filter()[0]
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = OfferStopSerializer(snippet, data=request.data)
        # print 'serializer= ', serializer
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class OfferLissageView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        cet = pytz.timezone('utc')
        company = self.request.query_params.get('company', None)
        cc = self.request.query_params.get('cc', None)
        years = self.request.query_params.get('years', '')
        percent = self.request.query_params.get('percent', None)
        if percent:
            percent = int(percent)
        years_list = years.split(',')
        data_year = int(datetime.now().year)-1
        transaction_years = map(lambda x: data_year + x, range(1,7))
        lissage_years = []
        non_lissage_years = []
        volumes = []
        price = []
        price_final = []
        decote_reporte = []
        lissage = []
        energies = []
        offer_base = None
        q = Q()
        coffer = Offer.objects.none()
        if years_list == ['']:
            years_list = []
        if cc:
            try:
                meter = Meter.objects.get(site_id=int(cc), meter_sum=True)
            except:
                return Response(OrderedDict([('lissage_years', lissage_years),
                                             ('years', map(lambda y: int(y), years_list)),
                                             ('volumes', volumes),
                                             ('prices', price),
                                             ('prices_final', price_final),
                                             ('decote_reporte', decote_reporte),
                                             ('lissage', lissage),
                                             ('energies', energies)
                                             ]), status=status.HTTP_204_NO_CONTENT)
            coffer = Offer.objects.filter(cc = meter)
            if not coffer:
                return Response(OrderedDict([('lissage_years', lissage_years),
                                             ('years', map(lambda y: int(y), years_list)),
                                             ('volumes', volumes),
                                             ('prices', price),
                                             ('prices_final', price_final),
                                             ('decote_reporte', decote_reporte),
                                             ('lissage', lissage),
                                             ('energies', energies)
                                             ]), status=status.HTTP_204_NO_CONTENT)
        if company:
            coffer = coffer.filter(company_id = int(company))
            if not coffer:
                return Response(OrderedDict([('lissage_years', lissage_years),
                                             ('years', map(lambda y: int(y), years_list)),
                                             ('volumes', volumes),
                                             ('prices', price),
                                             ('prices_final', price_final),
                                             ('decote_reporte', decote_reporte),
                                             ('lissage', lissage),
                                             ('energies', energies)
                                             ]), status=status.HTTP_204_NO_CONTENT)

        if years_list != [''] and cc and company:
            meter = Meter.objects.get(site_id=int(cc), meter_sum=True)
            # print 'yes', meter
            sum_decode = []
            non_lissage = 0
            lnon_lissage = []
            volumes_non_lissage = []
            for y in sorted(years_list):
                lissage_offer = Offer.objects.filter(years__icontains = y, cc = meter, company_id = int(company), lissage=True, offer_status='signee')
                if len(y) == 4 and y.isdigit():
                    data_from = cet.localize(datetime(int(y), 01, 01, 0, 0), is_dst=None)
                    data_to = cet.localize(datetime(int(y), 12, 31, 23, 59), is_dst=None)
                    if int(y) in transaction_years:
                        cc_data = TranslationRecord.objects.filter(meter = meter,
                                                            interval_start__gte=data_from,
                                                            interval_start__lte=data_to
                                                            ).aggregate(Sum('value'))
                        volumes.append({y: "{:,}".format(int(round(cc_data['value__sum']))).replace(",", "'") })
                        # volumes.append({y: cc_data['value__sum'] })
                    else:
                        cc_data = EnergyConsumptionRecord.objects.filter(meter = meter,
                                                                interval_start__gte=data_from,
                                                                interval_start__lte=data_to
                                                                ).aggregate(Sum('value'))
                        volumes.append({y: "{:,}".format(int(round(cc_data['value__sum']))).replace(",", "'") })
                        # volumes.append({y: cc_data['value__sum'] })
                    try:
                        lissage_offer = Offer.objects.filter(years__icontains = y, cc = meter, company_id = int(company), lissage=True, offer_status='signee')
                        loffer = Offer.objects.filter(years__icontains=y, cc=meter, company_id=int(company), lissage=False, offer_status='signee').exclude(lis_force=True, lis_manual_expire__lte=datetime.now())
                        # liage_offer = Offer.objects.filter(years__icontains = y, cc = meter, company_id = int(company), lissage=True)
                        # print 'lissage_offer = ', re.sub('\'','\"',lissage_offer[0].lissage_years)
                        if loffer.exists() and lissage_offer.exists() == False:
                            lissage_years.append(int(y))
                            for offer in loffer:
                                budget = Budget.objects.filter(year=int(y), offer=offer).order_by('-created')[0]
                                offer_base = offer.id
                                print 'offer === ', y, offer, budget
                                price.append({y: BudgetAveragePerYear.objects.get(year=int(y), budget=budget).value})
                                price_final.append({y: BudgetAveragePerYearRiscs.objects.get(year=int(y), budget=budget).value})
                                average_year = BudgetAveragePerYearRiscs.objects.get(year=int(y), budget=budget).value
                                decode = ((average_year * cc_data['value__sum']) * (float(percent) / 100)) / 100
                                decode_round = int(round(decode))
                                print decode_round
                                decote_reporte.append({y: decode_round})
                                sum_decode.append(decode)
                                if ParameterRecord.objects.get(parameter=Parameter.objects.get(code='energies'), year=int(y), offer=offer).value != 0:
                                    energies.append(int(y))
                        else:
                            # print 'loffer.exists()', y
                            non_lissage_years.append(int(y))
                            non_lissage = non_lissage + 1
                            if cc_data['value__sum'] == None:
                                lnon_lissage.append({y: 0})
                                volumes_non_lissage.append(0)
                            else:
                                lnon_lissage.append({y: cc_data['value__sum']})
                                volumes_non_lissage.append(cc_data['value__sum'])
                            print 'sum = ', y, sum(sum_decode), 'non_lissage = ', non_lissage, cc_data['value__sum'], float(percent) / 100
                    except:
                        pass
            print 'lnon_lissage', lnon_lissage
            for liss in lnon_lissage:
                for key in liss.keys():
                    try:
                        lissage.append({key: (((sum(sum_decode) / sum(volumes_non_lissage)) * 100) *(-1))})
                        # print(key, (sum(sum_decode) / sum(volumes_non_lissage)))
                    except:
                        lissage = []
        return Response(OrderedDict([('lissage_years', lissage_years),
                                     ('years', sorted(non_lissage_years)),
                                     ('volumes', volumes),
                                     ('prices', price),
                                     ('prices_final', price_final),
                                     ('decote_reporte', decote_reporte),
                                     ('lissage', lissage),
                                     ('energies', energies),
                                     ('offer', offer_base)
                                     ]), status=status.HTTP_200_OK)


class OffersViewSet(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)


    def generate_sme_mail(self, obj):
        cet = pytz.timezone('UTC')
        offer = Offer.objects.get(id=obj)
        energy_med = EnergyConsumptionRecord.objects.filter(meter=offer.cc).only('interval_start', 'value').order_by('interval_start')
        meds = TranslationRecord.objects.filter(meter=offer.cc).only('interval_start', 'value').order_by('interval_start')
        year = energy_med[0].interval_start.year
        print 'year = ', year, offer.pfc_market
        base = HeadgeRecord.objects.get(meter=offer.cc, year=int(year), schedule=Shedule.objects.get(title='OffPeak')).value
        peak = HeadgeRecord.objects.get(meter=offer.cc, year=int(year), schedule=Shedule.objects.get(title='Peak')).value - base

        ps1 = ParameterRecord.objects.filter(offer=obj, parameter=Parameter.objects.get(code='ps1')).values_list('value', flat=True)
        ps2 = ParameterRecord.objects.filter(offer=obj, parameter=Parameter.objects.get(code='ps2')).values_list('value', flat=True)
        exists_ps1 = sum(list(ps1)) != 0
        exists_ps2 = sum(list(ps2)) != 0

        year_sum = defaultdict()

        for year in offer.years_list:
            # data_from = cet.localize(datetime(int(year), 01, 01, 0, 0), is_dst=None)
            # data_to = cet.localize(datetime(int(year), 12, 31, 23, 59), is_dst=None)

            if offer.pfc_date_first:
                fdate = make_naive(offer.pfc_date_first, pytz.timezone('CET'))
                if fdate.year == int(year):
                    data_from = cet.localize(datetime(int(year), fdate.month, fdate.day, 0, 0), is_dst=None)
                else:
                    data_from = cet.localize(datetime(int(year), 01, 01, 0, 0), is_dst=None)
            else:
                data_from = cet.localize(datetime(int(year), 01, 01, 0, 0), is_dst=None)
            
            if offer.pfc_date_last:
                ldate = make_naive(offer.pfc_date_last, pytz.timezone('CET'))
                if ldate.year == int(year):
                    data_to = cet.localize(datetime(int(year), ldate.month, ldate.day, 23, 59), is_dst=None)
                else:
                    data_to = cet.localize(datetime(int(year), 12, 31, 23, 59), is_dst=None)
            else:
                data_to = cet.localize(datetime(int(year), 12, 31, 23, 59), is_dst=None)
            
            
            energ_sum = meds.filter(interval_start__gte=data_from, interval_start__lte=data_to).aggregate(Sum('value'))
            print(meds.filter(interval_start__gte=data_from, interval_start__lte=data_to))
            if energ_sum == None:
                energ_sum = energy_med.filter(interval_start__gte=data_from, interval_start__lte=data_to).aggregate(Sum('value'))
                
            print data_from, data_to
            
            year_sum[int(year)] = "{:,}".format(int(round(energ_sum['value__sum']))).replace(",", "'")

        # year_sum = {
        #     k: "{:,}".format(int(round(sum(x.value for x in g)))).replace(",", "'")
        #     for k, g in groupby(list(meds)+list(energy_med), key=lambda i: i.interval_start.year)
        # }

        print 'year_sum = ', year_sum
        context = {
            "offer": offer,
            "years": [int(x) for x in offer.years_list],
            "year_sum": year_sum,
            "unit": offer.unit,
            "peak": peak/float(1000),
            "base": base/float(1000),
            "exists_ps1": exists_ps1,
            "exists_ps2": exists_ps2,
        }
        template = get_template('tool/mail/email-sme.html')
        email_content = template.render(context)
        # print email_content
        return email_content



    def get(self, request, format=None):
        stare = self.request.query_params.get('stare', '')
        year = self.request.query_params.get('year', None)
        name = self.request.query_params.get('name', None)
        nr = self.request.query_params.get('nr', None)
        pag = self.request.query_params.get('pag', 1)
        cockpit = self.request.query_params.get('cockpit', None)
        last = 0
        first = 0
        q = Q()
        if cockpit:
            if cockpit.lower() == 'true':
                cockpit = True
                q &= Q(offer_status='indicative')
            elif  cockpit.lower() == 'false':
                cockpit = False
            q &= Q(cockpit = cockpit)
        if stare != '':
            q &= Q(offer_status = str(stare))
        if name != None:
            firstname = name.split(' ')[0]
            # q &= Q(Q(name__icontains=str(firstname)) | Q(company__nom_entrepise__icontains=str(firstname))
            #        | Q(company__name__icontains=str(firstname)) | Q(user__first_name__icontains=str(firstname)) | Q(user__last_name__icontains=str(firstname)))
            
            print 'firstname == ', firstname
            
            try:
                eid = int(name)
                q &= Q(Q(emp_id__icontains=eid) | Q(id__icontains=eid))
            except:
                try:
                    print 'lastname == ', lastname
                    lastname = name.split(' ')[1]
                    if lastname != '':
                        # q &= Q(Q(user__first_name__icontains=str(firstname)) | Q(user__last_name__icontains=str(lastname)))
                        q &= Q(Q(name__icontains=str(firstname)) | Q(company__nom_entrepise__icontains=str(firstname))
                            | Q(company__name__icontains=str(firstname)) | Q(user__first_name__icontains=str(firstname)) 
                            | Q(user__last_name__icontains=str(lastname)))
                except:
                    # q &= Q(Q(user__first_name__icontains=str(firstname)) | Q(user__last_name__icontains=str(firstname)))
                    q &= Q(Q(name__icontains=str(firstname)) | Q(company__nom_entrepise__icontains=str(firstname))
                        | Q(company__name__icontains=str(firstname)) | Q(user__first_name__icontains=str(firstname)) 
                        | Q(user__last_name__icontains=str(firstname)))

            # try:
            #     eid = int(name)
            #     q &= Q(Q(emp_id=eid))
            # except:
            #     print('no edit')
        
        if year != None:
            if len(year) == 4 and year.isdigit():
                q &= Q(created__year = int(year))
        snippets = Offer.objects.filter(q).filter(lis_force=False).order_by('-pk')
        
        if nr:
            per_page = int(nr)
        else:
            per_page = 10

        if int(len(snippets)) % per_page == 0:
            leng = len(snippets)/per_page
        else :
            leng = len(snippets)/per_page + 1
        if pag == leng:
            first = int(len(snippets)/per_page)*per_page
            last = len(snippets)
        else:
            if int(pag) == 1 :
                first = 0
                last = per_page
            else :
                last = int(pag) * per_page
                first = last - per_page
        print first, last
        serializer = OfferMetersSerializer(snippets[first:last], context={"request": request}, many=True)
        return Response(OrderedDict([('pages', leng),
                                     ('pag', int(pag)),
                                     ('result', serializer.data)]),
                        status=status.HTTP_200_OK)


    def post(self, request, format=None):
        try:
            ip = request.META.get('HTTP_X_REAL_IP')
        except:
            ip = request.META.get('REMOTE_ADDR')
        g = GeoIP2()
        country = ''
        city = ''
        latitude = 0
        longitude = 0
        if str(ip) != '127.0.0.1' and ip:
            try:
                print g.city(ip)
                if g.city(ip)['country_code'] == 'MD':
                    country = 'RO'
                    city = 'Iasi'
                    latitude = 47.1584549
                    longitude = 27.6014418
                else:
                    country = g.city(ip)['country_code']
                    city = g.city(ip)['city']
                    latitude = g.city(ip)['latitude']
                    longitude = g.city(ip)['longitude']
            except:
                country = ''
                city = ''

        print 'offer = ', request.data
        cet = pytz.timezone('UTC')
        try:
            stop = OfferStop.objects.all()[0]
            if stop.stop == True:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if request.data['offer_type'] == 'SME':
            # print request.data['date_debut']['date']['year']
            date_debut = datetime(request.data['date_debut']['date']['year'],
                                               request.data['date_debut']['date']['month'],
                                               request.data['date_debut']['date']['day'],
                                               int(request.data['heures_in'][:2]),
                                               int(request.data['heures_in'][3:])
                                               )
            date_fin = datetime(request.data['date_fin']['date']['year'],
                                               request.data['date_fin']['date']['month'],
                                               request.data['date_fin']['date']['day'],
                                               int(request.data['heures_fin'][:2]),
                                               int(request.data['heures_fin'][3:])
                                               )
            # print date_debut, date_fin
            request.data.pop('heures_in', None)
            request.data.pop('heures_fin', None)
            request.data['date_debut'] = date_debut
            request.data['date_fin'] = date_fin
        else:
            request.data['date_debut'] = None
            request.data['date_fin'] = None
        
        try:
            pfc_date_first = datetime(request.data['pfc_date_first']['date']['year'],
                                        request.data['pfc_date_first']['date']['month'],
                                        request.data['pfc_date_first']['date']['day'],
                                        0, 0)
            
            pfc_date_last = datetime(request.data['pfc_date_last']['date']['year'],
                                        request.data['pfc_date_last']['date']['month'],
                                        request.data['pfc_date_last']['date']['day'],
                                        23, 59)
            request.data['pfc_date_first'] = pfc_date_first
            request.data['pfc_date_last'] = pfc_date_last
        except:
            request.data['pfc_date_first'] = None
            request.data['pfc_date_last'] = None

        user = request.data['user']
        if request.data['conseiller']:
            request.data['user'] = request.data['conseiller']
            request.data['conseiller'] = user
        
        try:
            admin = User.objects.get(id=int(request.data['user']))
        except:
            admin = None
        
        site = request.data['cc']
        del request.data['cc']
        years = ','.join(str(e) for e in request.data['years'])
        lis_years = ','.join(str(e) for e in request.data['lis_years'])
        request.data['years'] = years
        request.data['lis_years'] = lis_years
        request.data['cc'] = Meter.objects.get(site_id = int(site), meter_sum=True).id
        serializer = OfferEditSerializer(data=request.data)
        # print serializer
        # print 'serializer.is_valid() == ', serializer.is_valid()
        if request.is_mobile or request.is_tablet or request.is_phone:
            device = 'mobile'
        else:
            device = 'desktop'
        if serializer.is_valid():
            serializer.save()
            if serializer.data['offer_type'] == 'SME':
                cl = ClientLog(offer_id=serializer.data['id'], client_id=serializer.data['company'], ip=str(ip), log_type='aconfirmer',
                               country=country, city=city, admin=admin, latitude=latitude, longitude=longitude, device=device)
                cl.save()
                email_content = self.generate_sme_mail(serializer.data['id'])
                
                # FROM = 'non.commodity.data@gmail.com'
                FROM = getattr(settings, 'MAIL_NAME')
                emails = []
                semails = list(SmeEmail.objects.all().values_list('email', flat=True))
                
                if str(request.get_host()) == str('localhost:8000'):
                    emails = ['n.botnaru@energymarketprice.com'] + semails
                else:
                    emails = ['v.diaconu@energymarketprice.com', 'n.botnaru@energymarketprice.com'] + semails
                
                for TO in emails:
                    py_mail(serializer.data['name'], email_content, [], TO, FROM)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OfferSendSMEMailView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def generate_sme_mail(self, obj):
        cet = pytz.timezone('UTC')
        offer = Offer.objects.get(id=obj)
        energy_med = EnergyConsumptionRecord.objects.filter(meter=offer.cc).only('interval_start', 'value').order_by('interval_start')
        meds = TranslationRecord.objects.filter(meter=offer.cc).only('interval_start', 'value').order_by('interval_start')
        year = energy_med[0].interval_start.year
        print 'year = ', year, offer.pfc_market
        base = HeadgeRecord.objects.get(meter=offer.cc, year=int(year), schedule=Shedule.objects.get(title='OffPeak')).value
        peak = HeadgeRecord.objects.get(meter=offer.cc, year=int(year), schedule=Shedule.objects.get(title='Peak')).value - base

        ps1 = ParameterRecord.objects.filter(offer=obj, parameter=Parameter.objects.get(code='ps1')).values_list('value', flat=True)
        ps2 = ParameterRecord.objects.filter(offer=obj, parameter=Parameter.objects.get(code='ps2')).values_list('value', flat=True)
        exists_ps1 = sum(list(ps1)) != 0
        exists_ps2 = sum(list(ps2)) != 0

        year_sum = defaultdict()

        for year in offer.years_list:
            # data_from = cet.localize(datetime(int(year), 01, 01, 0, 0), is_dst=None)
            # data_to = cet.localize(datetime(int(year), 12, 31, 23, 59), is_dst=None)

            if offer.pfc_date_first:
                fdate = make_naive(offer.pfc_date_first, pytz.timezone('CET'))
                if fdate.year == int(year):
                    data_from = cet.localize(datetime(int(year), fdate.month, fdate.day, 0, 0), is_dst=None)
                else:
                    data_from = cet.localize(datetime(int(year), 01, 01, 0, 0), is_dst=None)
            else:
                data_from = cet.localize(datetime(int(year), 01, 01, 0, 0), is_dst=None)
            
            if offer.pfc_date_last:
                ldate = make_naive(offer.pfc_date_last, pytz.timezone('CET'))
                if ldate.year == int(year):
                    data_to = cet.localize(datetime(int(year), ldate.month, ldate.day, 23, 59), is_dst=None)
                else:
                    data_to = cet.localize(datetime(int(year), 12, 31, 23, 59), is_dst=None)
            else:
                data_to = cet.localize(datetime(int(year), 12, 31, 23, 59), is_dst=None)
            
            
            energ_sum = meds.filter(interval_start__gte=data_from, interval_start__lte=data_to).aggregate(Sum('value'))
            print(meds.filter(interval_start__gte=data_from, interval_start__lte=data_to))
            if energ_sum == None:
                energ_sum = energy_med.filter(interval_start__gte=data_from, interval_start__lte=data_to).aggregate(Sum('value'))
                
            print data_from, data_to
            
            year_sum[int(year)] = "{:,}".format(int(round(energ_sum['value__sum']))).replace(",", "'")

        # year_sum = {
        #     k: "{:,}".format(int(round(sum(x.value for x in g)))).replace(",", "'")
        #     for k, g in groupby(list(meds)+list(energy_med), key=lambda i: i.interval_start.year)
        # }

        print 'year_sum = ', year_sum
        context = {
            "offer": offer,
            "years": [int(x) for x in offer.years_list],
            "year_sum": year_sum,
            "unit": offer.unit,
            "peak": peak/float(1000),
            "base": base/float(1000),
            "exists_ps1": exists_ps1,
            "exists_ps2": exists_ps2,
        }
        template = get_template('tool/mail/email-sme.html')
        email_content = template.render(context)
        # print email_content
        return email_content


    def post(self, request, pk, format=None):
        email_content = self.generate_sme_mail(int(pk))

        try:
            offer = Offer.objects.get(id=int(pk))
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # FROM = 'non.commodity.data@gmail.com'
        FROM = getattr(settings, 'MAIL_NAME')
        emails = []
        semails = list(SmeEmail.objects.all().values_list('email', flat=True))

        if str(request.get_host()) == str('localhost:8000'):
            emails = ['n.botnaru@energymarketprice.com'] + semails
        else:
            emails = ['v.diaconu@energymarketprice.com',
                        'n.botnaru@energymarketprice.com'] + semails
        for TO in emails:
            print('send sme', TO)
            py_mail(offer.name, email_content, [], TO, FROM)
        return Response({'result': 'Email was send'}, status=status.HTTP_200_OK)


class OfferByCompanyViewSet(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, company, format=None):
        cc = self.request.query_params.get('cc', None)
        year = self.request.query_params.get('year', None)
        name = self.request.query_params.get('name', None)
        pag = self.request.query_params.get('pag', 1)
        nr = self.request.query_params.get('nr', None)
        last = 0
        first = 0
        if nr:
            per_page = int(nr)
        else:
            per_page = 10
        print cc, year, name
        q = Q(company_id = company)
        snippets = []
        if name != None:
            # q &= Q(name__icontains = str(name))
            firstname = name.split(' ')[0]
            # q &= Q(Q(name__icontains=str(firstname)) | Q(company__nom_entrepise__icontains=str(firstname))
            #        | Q(company__name__icontains=str(firstname)) | Q(user__first_name__icontains=str(firstname)) | Q(user__last_name__icontains=str(firstname)))
            # print 'firstname == ', firstname
            try:
                # print 'lastname == ', lastname
                lastname = name.split(' ')[1]
                if lastname != '':
                    # q &= Q(Q(user__first_name__icontains=str(firstname)) | Q(user__last_name__icontains=str(lastname)))
                    q &= Q(Q(name__icontains=str(firstname)) | Q(company__nom_entrepise__icontains=str(firstname))
                           | Q(company__name__icontains=str(firstname)) | Q(user__first_name__icontains=str(firstname)) | Q(user__last_name__icontains=str(lastname)))
            except:
                # q &= Q(Q(user__first_name__icontains=str(firstname)) | Q(user__last_name__icontains=str(firstname)))
                q &= Q(Q(name__icontains=str(firstname)) | Q(company__nom_entrepise__icontains=str(firstname))
                       | Q(company__name__icontains=str(firstname)) | Q(user__first_name__icontains=str(firstname)) | Q(user__last_name__icontains=str(firstname)))

        
        if cc:
            q &= Q(cc__site_id = int(cc))
        if year != None:
            if len(year) == 4 and year.isdigit():
                q &= Q(created__year = int(year))
                snippets = Offer.objects.filter(q).filter(lis_force=False).order_by('-pk')
        else:
            snippets = Offer.objects.filter(q).filter(lis_force=False).order_by('-pk')

        if int(len(snippets)) % per_page == 0:
            leng = len(snippets)/per_page
        else :
            leng = len(snippets)/per_page + 1
        if pag == leng:
            first = int(len(snippets)/per_page)*per_page
            last = len(snippets)
        else:
            if int(pag) == 1 :
                first = 0
                last = per_page
            else :
                last = int(pag) * per_page
                first = last - per_page
        print first, last
        serializer = OfferMetersSerializer(snippets[first:last], context={"request": request}, many=True)
        return Response(OrderedDict([('pages', leng),
                                     ('pag', int(pag)),
                                     ('result', serializer.data)]),
                        status=status.HTTP_200_OK)


class OfferListByCompanyViewSet(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, company, format=None):
        cockpit = self.request.query_params.get('cockpit', None)
        q = Q()
        if cockpit:
            if cockpit.lower() == 'true':
                cockpit = True
            elif cockpit.lower() == 'false':
                cockpit = False
            q &= Q(cockpit = cockpit)
        snippets = Offer.objects.filter(company_id=company, lis_force=False).filter(q)
        serializer = OfferSerializer(snippets, context={"request": request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class OfferByIdView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, pk, format=None):
        snippet = get_object_or_404(Offer, pk=pk)
        serializer = OfferSerializer(snippet)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        if request.get_host() == '79.137.34.74':
            url = request.scheme + '://' + 'energysalesdirect.com:9090'
        else:
            url = request.scheme + '://' + request.get_host()
        snippet = get_object_or_404(Offer, pk=pk)
        if snippet.offer_type == 'SME':
            print('sme')
            request.data.pop('showStatusPopup')
            request.data.pop('user')
            request.data.pop('pfc')
            request.data['id'] = snippet.id
            # print request.data
            serializer = OfferEditPfcMarketSerializer(snippet, data=request.data)
            print 'validates=', serializer.is_valid()
            # print serializer.validated_data
            if serializer.is_valid():
                serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            serializer = OfferEditNameSerializer(snippet, data=request.data)
            if serializer.is_valid():
                serializer.save()
                for sign in snippet.signatures.all():
                    email_content = generate_email_content(snippet, 'fonction', url, sign)
                    TO = sign.email
                    FROM = getattr(settings, 'MAIL_NAME')
                    py_mail(snippet.name, email_content, [], TO, FROM)
                return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        snippet = get_object_or_404(Offer, pk=pk)
        if snippet.offer_status == 'supprimer':
            snippet.delete()
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class OfferByIdCockpitView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk, format=None):
        snippet = get_object_or_404(Offer, pk=pk)
        serializer = OfferEditCockpitSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OfferByPfcEnergyView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        code = self.request.query_params.get('code', None)
        pfc = self.request.query_params.get('pfc', None)
        market = self.request.query_params.get('market', 'false')
        print market
        try:
            if market.lower() == 'true':
                risce = RiscRecord.objects.filter(pfc_market_id=int(pfc), risc__code=code).values('risc__name', 'year', 'value')
            else:
                risce = RiscRecord.objects.filter(pfc_id=int(pfc), risc__code=code).values('risc__name', 'year', 'value')
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(list(risce), status=status.HTTP_200_OK)


class OfferByIdCockpitYearsView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def isValue(self, value, default):
        # print 'value', value
        if not value:
            return default
        else:
            return value

    def get(self, request, pk, format=None):
        try:
            years = Offer.objects.get(id=pk).years.split(',')
            print years
            offer = Offer.objects.get(id=int(pk))
            if offer.pfc_market:
                budgets = Budget.objects.filter(offer=offer, pfc_market=offer.pfc_market).values_list('id', flat=True)
            else:
                budgets = Budget.objects.filter(offer=offer, pfc=offer.pfc).values_list('id', flat=True)
        except:
            return Response(status=status.HTTP_204_NO_CONTENT)

        # try:
        #     snippets = PFC.objects.all().exclude(time=None).exclude(time='')
        #     reg_list = [{'id': pfc.id, 'pfc_id': datetime.strptime(pfc.pfc_id, '%d.%m.%Y'), 'created': pfc.created} for pfc in list(snippets)]
        #     records_list = sorted(reg_list, key=lambda x: x['pfc_id'], reverse=True)
        #     # print(records_list)
        #     data_riscs = [{'id': pfc['id'], 'pfc_id':  pfc['pfc_id'].strftime('%d.%m.%Y'), 'created': pfc['created']} for pfc in records_list]
        #     pfc = data_riscs[0]
        # except:
        #     return Response(status=status.HTTP_204_NO_CONTENT)
        # meds = PfcConsumptionRecord.objects.filter(pfc=offer.pfc).only('interval_start', 'value').order_by('interval_start')
        # if not meds:
        #     return Response(status=status.HTTP_204_NO_CONTENT)
        # year_nr = {
        #     k: len(list(g))
        #     for k, g in groupby(meds, key=lambda i: i.interval_start.year)
        # }
        # year_sum = {
        #     k: sum(x.value for x in g)
        #     for k, g in groupby(meds, key=lambda i: i.interval_start.year)
        # }

        year_sum = defaultdict()
        years = map(lambda x:int(x), years)
        price_final = BudgetAveragePerYearRiscs.objects.filter(budget__in=budgets, year__in=years).values('year', 'value')
        for price in price_final:
            year_sum[price['year']] = price['value']

        data = []
        today = datetime.now().date()
        last_day = datetime.now().date().replace(month=12, day=31)
        # print year_nr, year_sum
        for year in years:
            try:
                cockpit = CockpitOffer.objects.get(year=int(year), offer_id=pk)
                if cockpit:
                    data.append({'year': year,
                             'value': float("{0:.2f}".format(year_sum[year])),
                             'highest': self.isValue(cockpit.highest, ''),
                             'lowest': self.isValue(cockpit.lowest, ''),
                             'date_from': self.isValue(cockpit.date_from, today),
                             'date_to': self.isValue(cockpit.date_to, last_day),
                             'email': cockpit.email,
                            })
            except:
                data.append({'year':year,
                             'value': float("{0:.2f}".format(year_sum[year])),
                             'highest': '',
                             'lowest': '',
                             'date_from': today,
                             'date_to': last_day,
                             'email': '',
                            })
                # data.append({'year':year,
                #              'value': float("{0:.2f}".format(year_sum[year]/ float(year_nr[year]))),
                #              'highest': float("{0:.2f}".format(year_sum[year]/ float(year_nr[year])))+10,
                #              'lowest': float("{0:.2f}".format((year_sum[year]/ float(year_nr[year]))-10)),
                #              'date_from': today,
                #              'date_to': last_day,
                #              'email': '',
                #             })
        return Response({'result':data}, status=status.HTTP_200_OK)


    def post(self, request, pk, format=None):
        try:
            obj = Offer.objects.get(id=pk)
        except:
            return Response({'result':'Offer not found'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            request.data['cockpit'][0]
        except:
            return Response({'result':'Cockpit not found'}, status=status.HTTP_400_BAD_REQUEST)

        if int(request.data['cockpit'][0]) > 1 and int(request.data['cockpit'][0]) < 9:
            print 'cockpits = ', request.data['cockpit']
            cpt = Cockpit.objects.get(id=2)
            CockpitOffer.objects.filter(offer=obj).delete()
            for cockpit_id in request.data['cockpit']:
                print 'cockpit_id = ', cockpit_id
                cockpit = CockpitOffer(cockpit=cpt, offer=obj, weekday = Weekday.objects.get(day=int(cockpit_id)-1))
                cockpit.save()
            return Response({'result':'Cockpit was created'}, status=status.HTTP_200_OK)
        if int(request.data['cockpit'][0]) == 1:
            # print 'obj == ', obj
            CockpitOffer.objects.filter(offer=obj).delete()
            for cockpit in request.data['result']:
                snippet, created = CockpitOffer.objects.update_or_create(cockpit_id=1,
                                                                            offer=obj,
                                                                            year=int(cockpit['year']),
                                                                        )
                CockpitOffer.objects.filter(id=snippet.id).update(highest=float(cockpit['highest']),
                                                                    lowest=float(cockpit['lowest']),
                                                                    date_from=cockpit['date_from'],
                                                                    date_to=cockpit['date_to'],
                                                                    email=cockpit['email'])
                # cockpit.pop('value', None)
                # print snippet, cockpit
                # serializer = CockpitFirstOfferSerializer(snippet, data=cockpit)
                # print serializer.is_valid()
                # if serializer.is_valid():
                #     print 'valid'
                #     serializer.save()
            return Response({'data': 'Cockpit was added'}, status=status.HTTP_200_OK)

        if int(request.data['cockpit'][0]) == 9:
            CockpitOffer.objects.filter(offer=obj).delete()
            snippet, created = CockpitOffer.objects.update_or_create(cockpit_id=3, offer=obj)
            return Response({'result':'Cockpit was created'}, status=status.HTTP_200_OK)
        return Response({'result':'Cockpit was created'}, status=status.HTTP_200_OK)


def generate_email_content(obj, destination, url, sign=None):
    cet = pytz.timezone('UTC')
    budgets = Budget.objects.filter(offer_id=obj.id, pfc=obj.pfc).values_list('id', flat=True)
    years = Budget.objects.filter(offer_id=obj.id, pfc=obj.pfc).values_list('year', flat=True)
    years = sorted(reduce(lambda r, v: v in r and r or r + [v], years, []))
    budget_season = BudgetMedSeasonWithRiscsRecord.objects.filter(budget__in=budgets,
                                                                   year__in=years,
                                                                   ).annotate(hp_hc=F('schedule__title')).values('year', 'value', 'season', 'schedule__id', 'hp_hc')

    average_year_price = BudgetAveragePerYearRiscs.objects.filter(budget__in=budgets, year__in=years).values('year', 'value')
    title_ids = BudgetMedSeasonRecord.objects.filter(budget__in=budgets, year__in=years).annotate(hp_hc_id=F('schedule__id')).values_list('hp_hc_id', flat=True)
    title_ids = sorted(reduce(lambda r, v: v in r and r or r + [v], title_ids, []))
    energy_med = EnergyConsumptionRecord.objects.filter(meter=obj.cc).only('interval_start', 'value').order_by('interval_start')
    meds = TranslationRecord.objects.filter(meter=obj.cc).only('interval_start', 'value').order_by('interval_start')
    from itertools import chain

    # energys = energy_med | meds

    if obj.offer_type == 'Standart':
        expiration_date = obj.expiration_date.replace(hour=23, minute=59).strftime('%d/%m/%Y %H:%M')
    else:
        # cet = pytz.timezone('UTC')
        interval_date_fin = pytz.utc.localize(datetime.strptime(str(obj.date_fin)[:16], '%Y-%m-%d %H:%M'))
        value = interval_date_fin.astimezone(pytz.timezone('CET'))
        expiration_date = value.strftime('%d/%m/%Y %H:%M')

    year_sum = defaultdict()

    for year in obj.years_list:
        # data_from = cet.localize(datetime(int(year), 01, 01, 0, 0), is_dst=None)
        # data_to = cet.localize(datetime(int(year), 12, 31, 23, 59), is_dst=None)

        if obj.pfc_date_first:
            fdate = make_naive(obj.pfc_date_first, pytz.timezone('CET'))
            if fdate.year == int(year):
                data_from = cet.localize(datetime(int(year), fdate.month, fdate.day, 0, 0), is_dst=None)
            else:
                data_from = cet.localize(datetime(int(year), 01, 01, 0, 0), is_dst=None)
        else:
            data_from = cet.localize(datetime(int(year), 01, 01, 0, 0), is_dst=None)
        
        if obj.pfc_date_last:
            ldate = make_naive(obj.pfc_date_last, pytz.timezone('CET'))
            if ldate.year == int(year):
                data_to = cet.localize(datetime(int(year), ldate.month, ldate.day, 23, 59), is_dst=None)
            else:
                data_to = cet.localize(datetime(int(year), 12, 31, 23, 59), is_dst=None)
        else:
            data_to = cet.localize(datetime(int(year), 12, 31, 23, 59), is_dst=None)
        
        
        energ_sum = meds.filter(interval_start__gte=data_from, interval_start__lte=data_to).aggregate(Sum('value'))
        print(meds.filter(interval_start__gte=data_from, interval_start__lte=data_to))
        if energ_sum == None:
            energ_sum = energy_med.filter(interval_start__gte=data_from, interval_start__lte=data_to).aggregate(Sum('value'))
            
        print data_from, data_to
        
        year_sum[int(year)] = "{:,}".format(int(round(energ_sum['value__sum']))).replace(",", "'")


    # year_sum = {
    #     k: "{:,}".format(int(round(sum(x.value for x in g)))).replace(",", "'")
    #     for k, g in groupby(list(meds)+list(energy_med), key=lambda i: i.interval_start.year)
    # }

    try:
        if obj.pfc_market:
            energys = RiscRecord.objects.filter(pfc_market=obj.pfc_market,
                                                risc=Risc.objects.get(code=obj.energy_type)
                                                ).values('year', 'value')
        else:
            energys = RiscRecord.objects.filter(pfc=obj.pfc,
                                                risc=Risc.objects.get(code=obj.energy_type)
                                                ).values('year', 'value')
    except:
        energys = []
    
    surgos = ParameterRecord.objects.filter(offer=obj, parameter=Parameter.objects.get(code='sur_go')).values('year', 'value')
    ensum = list(energys) + list(surgos)
    
    totals_energy = []
    for year in years:
        totals_energy.append({"year": year, "value": sum(eitem['value'] for eitem in list(filter(lambda eco: eco['year'] == year, ensum)))})

    if obj.lissage:
        years_lis = [int(year) for year in obj.years_liss_list]
    else:
        years_lis = years

    try:
        pdf_logo = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media/logo/logo_zeno.png')
        with open(pdf_logo, "rb") as lfile:
            encoded_logo = base64.b64encode(lfile.read())
    except:
        encoded_logo = ''
    
    print 'encoded_logo', encoded_logo
    # print year_sum
    user = Company.objects.get(id=obj.company.id).id
    address = url + "/api/user/mail/?user=" + str(user) + "&offer=" + str(obj.unique_id)
    # print address, obj.user
    profile = Profile.objects.get(user=obj.user)
    try:
        sign_profile = Profile.objects.get(user=sign)
    except:
        sign_profile = None
    from django.utils.encoding import smart_str, smart_unicode
    context = {
                "budget_season": list(budget_season),
                "energys": list(totals_energy),
                "year_sum": year_sum,
                "prices": list(average_year_price),
                "years": years,
                "years_lis": years_lis,
                "customer": obj.company.name,
                "surname": obj.company.surname,
                "offer": obj.id,
                "token": obj.token,
                "offer": obj.name,
                "profile": profile,
                "sign_profile": sign_profile,
                "volumetrie": round(float(obj.volumetrie), 2),
                "omarge": round(float((obj.marge) - 100), 2),
                "obj": obj,
                "destination": destination,
                "titles": len(list(obj.shedules.all().values_list('id', flat=True))),
                "mail_address": address,
                "sign": sign,
                "expiration_date": expiration_date,
                "encoded_logo": encoded_logo,
                "url": url
              }
    print 'context === ', context
    template = get_template('tool/mail/email.html')
    email_content = template.render(context)
    # print email_content
    return email_content



class OfferSendMailByIdView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)


    def post(self, request, pk, format=None):
        try:
            stop = OfferStop.objects.all()[0]
            if stop.stop == True:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        from django.core.mail import EmailMessage
        try:
            obj = Offer.objects.get(id=pk)
        except:
            return Response({'result':'Offer not found'}, status=status.HTTP_400_BAD_REQUEST)
        print 'try client sent email data'
        
        if obj.offer_type == 'Standart' and obj.offer_status == 'indicative' and obj.expiration_date.date() < datetime.now().date():
            pfc = get_last_pfc()
            if obj.pfc != pfc:
                odata = {
                    'id': obj,
                    'pfc': pfc.id
                }
                try:
                    obj.expiration_date = expiration_date(obj.validation_time)
                    serializer = OfferPfcEditSerializer(obj, data=odata)
                    print 'valid = ', obj, serializer.is_valid()
                    if serializer.is_valid():
                        serializer.save()
                except:
                    print('error on update')
        
        try:
            ip = request.META.get('HTTP_X_REAL_IP')
        except:
            ip = request.META.get('REMOTE_ADDR')
        g = GeoIP2()
        country = ''
        city = ''
        latitude = 0
        longitude = 0
        # print g.city('109.185.174.82'), g.city('109.185.174.82')['latitude'], g.city('109.185.174.82')['longitude']
        if str(ip) != '127.0.0.1' and ip:
            try:
                print g.city(ip)
                if g.city(ip)['country_code'] == 'MD':
                    country = 'RO'
                    city = 'Iasi'
                    latitude = 47.1584549
                    longitude = 27.6014418
                else:
                    country = g.city(ip)['country_code']
                    city = g.city(ip)['city']
                    latitude = g.city(ip)['latitude']
                    longitude = g.city(ip)['longitude']
            except:
                country = ''
                city = ''
        
        if obj.expiration_date.date() < datetime.now().date():
            obj.expiration_date = expiration_date(obj.validation_time)
            obj.save()

        try:
            admin = User.objects.get(id=int(request.data['userId']))
        except:
            admin = None
        
        if request.get_host() == '79.137.34.74':
            url = request.scheme + '://' + 'energysalesdirect.com:9090'
        else:
            url = request.scheme + '://' + request.get_host()
        
        Offer.objects.filter(id=obj.id).update(token=uuid.uuid4(), mail_date=datetime.now())
        obj = Offer.objects.get(id=obj.id)
        if request.is_mobile or request.is_tablet or request.is_phone:
            device = 'mobile'
        else:
            device = 'desktop'

        cl = ClientLog(offer=obj, client=obj.company, ip=str(ip), log_type='send', device=device,
                       country=country, city=city, admin=admin, latitude=latitude, longitude=longitude)
        cl.save()
        email_content = generate_email_content(obj, 'client', url)
        TO = Company.objects.get(id=obj.company.id).email
        FROM = getattr(settings, 'MAIL_NAME')
        # FROM ='non.commodity.data@gmail.com'
        emails = obj.emails_list + [str(TO)]
        print emails
        for mail in emails:
            if mail != '':
                py_mail(obj.name, email_content, [], str(mail), FROM)
        
        return Response({'result':'Email was send'}, status=status.HTTP_200_OK)



class OfferSendFonctionMailByIdView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk, format=None):
        try:
            ip = request.META.get('HTTP_X_REAL_IP')
        except:
            ip = request.META.get('REMOTE_ADDR')

        g = GeoIP2()
        country = ''
        city = ''
        latitude = 0
        longitude = 0
        # print g.city('109.185.174.82'), g.city('109.185.174.82')['latitude'], g.city('109.185.174.82')['longitude']
        if str(ip) != '127.0.0.1' and ip:
            try:
                print g.city(ip)
                if g.city(ip)['country_code'] == 'MD':
                    country = 'RO'
                    city = 'Iasi'
                    latitude = 47.1584549
                    longitude = 27.6014418
                else:
                    country = g.city(ip)['country_code']
                    city = g.city(ip)['city']
                    latitude = g.city(ip)['latitude']
                    longitude = g.city(ip)['longitude']
            except:
                country = ''
                city = ''
        if request.is_mobile or request.is_tablet or request.is_phone:
            device = 'mobile'
        else:
            device = 'desktop'
        try:
            obj = Offer.objects.get(id=pk)
        except:
            return Response({'result': 'Offer not found'}, status=status.HTTP_400_BAD_REQUEST)
        print 'try sent email data'
        if request.get_host() == '79.137.34.74':
            url = request.scheme + '://' + 'energysalesdirect.com:9090'
        else:
            url = request.scheme + '://' + request.get_host()
        obj = Offer.objects.get(id=obj.id)
        obj.lis_force = False
        obj.save()
        if obj.offer_type == 'Standart':
            cl = ClientLog(offer=obj, client=obj.company, ip=str(ip), log_type='aconfirmer',
                        country=country, city=city, admin=obj.user, latitude=latitude, longitude=longitude, device=device)
            cl.save()
        
        for sign in obj.signatures.all():
            email_content = generate_email_content(obj, 'fonction', url, sign)
            TO = sign.email
            # FROM = 'non.commodity.data@gmail.com'
            FROM = getattr(settings, 'MAIL_NAME')
            py_mail(obj.name, email_content, [], TO, FROM)
        return Response({'result': 'Email was send'}, status=status.HTTP_200_OK)



class OfferSendAdminMailByIdView(APIView):
    # authentication_classes = (JSONWebTokenAuthentication, )
    # permission_classes = (IsAuthenticated,)

    def render_email_pdf(self, obj, url):
        cet = pytz.timezone('UTC')
        import pdfkit
        try:
            if obj.pfc_market:
                energys = RiscRecord.objects.filter(pfc_market=obj.pfc_market,
                                                    risc=Risc.objects.get(code=obj.energy_type)
                                                    ).values('year', 'value', 'risc')
            else:
                energys = RiscRecord.objects.filter(pfc=obj.pfc,
                                                    risc=Risc.objects.get(code=obj.energy_type)
                                                    ).values('year', 'value', 'risc')
        except:
            energies = []

        majors = ParameterRecord.objects.filter(
            offer=obj, parameter=Parameter.objects.get(code='sur_go')).values('year', 'value')

        # print 'energies === ', obj.pfc, energies
        # energys = defaultdict()
        energies = []

        for major in majors:
            for energy in energys:
                if int(energy['year']) == int(major['year']):
                    if major['value']:
                        # energys[str(energy['year'])] = energy['value'] + major['value']
                        energies.append({'year': energy['year'],
                                         'value': energy['value'] + major['value']})
                    else:
                        energies.append({'year': energy['year'], 'value': energy['value']})
                        # energys[str(energy['year'])] = energy['value']

        # print 'energies ===== ', energies

        energy_med = EnergyConsumptionRecord.objects.filter(meter=obj.cc).only(
            'interval_start', 'value').order_by('interval_start')

        meds = TranslationRecord.objects.filter(meter=obj.cc).only(
            'interval_start', 'value').order_by('interval_start')

        year_sum = defaultdict()

        for year in obj.years_list + [str(obj.cc.site.year)]:
            # data_from = cet.localize(datetime(int(year), 01, 01, 0, 0), is_dst=None)
            # data_to = cet.localize(datetime(int(year), 12, 31, 23, 59), is_dst=None)

            if obj.pfc_date_first:
                fdate = make_naive(obj.pfc_date_first, pytz.timezone('CET'))
                if fdate.year == int(year):
                    data_from = cet.localize(
                        datetime(int(year), fdate.month, fdate.day, 0, 0), is_dst=None)
                else:
                    data_from = cet.localize(datetime(int(year), 01, 01, 0, 0), is_dst=None)
            else:
                data_from = cet.localize(datetime(int(year), 01, 01, 0, 0), is_dst=None)

            if obj.pfc_date_last:
                ldate = make_naive(obj.pfc_date_last, pytz.timezone('CET'))
                if ldate.year == int(year):
                    data_to = cet.localize(datetime(int(year), ldate.month,
                                                    ldate.day, 23, 59), is_dst=None)
                else:
                    data_to = cet.localize(datetime(int(year), 12, 31, 23, 59), is_dst=None)
            else:
                data_to = cet.localize(datetime(int(year), 12, 31, 23, 59), is_dst=None)

            if str(year) == str(obj.cc.site.year):
                energ_sum = energy_med.filter(
                    interval_start__gte=data_from, interval_start__lte=data_to).aggregate(Sum('value'))
            else:
                energ_sum = meds.filter(interval_start__gte=data_from,
                                        interval_start__lte=data_to).aggregate(Sum('value'))
            # print(meds.filter(interval_start__gte=data_from, interval_start__lte=data_to))
            # print data_from, data_to

            # if energ_sum == None:
            #     energ_sum = energy_med.filter(interval_start__gte=data_from, interval_start__lte=data_to).aggregate(Sum('value'))

            year_sum[int(year)] = "{:,}".format(
                int(round(energ_sum['value__sum']))).replace(",", "'")

        # year_sum = {
        #     k: "{:,}".format(int(round(sum(x.value for x in g)))).replace(",", "'")
        #     for k, g in groupby(list(meds) + list(energy_med), key=lambda i: i.interval_start.year)
        # }
        # print year_sum
        print obj.meters
        if obj.offer_type == 'Standart':
            expiration_date = obj.expiration_date.replace(hour=23, minute=59).strftime('%d.%m.%Y %H:%M')
        else:
            # cet = pytz.timezone('UTC')
            interval_date_fin = pytz.utc.localize(datetime.strptime(str(obj.date_fin)[:16], '%Y-%m-%d %H:%M'))
            value = interval_date_fin.astimezone(pytz.timezone('CET'))
            expiration_date = value.strftime('%d.%m.%Y %H:%M')

        if obj.pfc_market:
            budgets = Budget.objects.filter(
                offer_id=obj.id, pfc_market=obj.pfc_market).values_list('id', flat=True)
            years = Budget.objects.filter(
                offer_id=obj.id, pfc_market=obj.pfc_market).values_list('year', flat=True)
        else:
            budgets = Budget.objects.filter(
                offer_id=obj.id, pfc=obj.pfc).values_list('id', flat=True)
            years = Budget.objects.filter(
                offer_id=obj.id, pfc=obj.pfc).values_list('year', flat=True)

        years = sorted(reduce(lambda r, v: v in r and r or r + [v], years, []))
        budget_season = BudgetMedSeasonWithRiscsRecord.objects.filter(budget__in=budgets,
                                                                      year__in=years).annotate(hp_hc=F('schedule__title')).values('year', 'value', 'season', 'hp_hc')
        title_ids = BudgetMedSeasonRecord.objects.filter(budget__in=budgets, year__in=years).annotate(
            hp_hc_id=F('schedule__id')).values_list('hp_hc_id', flat=True)
        title_ids = sorted(reduce(lambda r, v: v in r and r or r + [v], title_ids, []))
        print 'lenght == ', len(list(title_ids))
        fyear = obj.years_list[0]
        lyear = obj.years_list[-1]
        offer_from = datetime(int(fyear), 01, 01, 0, 0)

        try:
            signature = Profile.objects.get(user=obj.signer)
            admin_sig = signature.signature
            
            pdf_sadmin = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media/{}'.format(str(admin_sig)))
            with open(pdf_sadmin, "rb") as sfile:
                encoded_admin = base64.b64encode(sfile.read())
        except:
            signature = Profile.objects.get(user=obj.user)
            admin_sig = ''
            encoded_admin = ''

        try:
            user_sign = Profile.objects.get(user=obj.user)
            user_sig = user_sign.signature
            pdf_suser = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media/{}'.format(str(user_sig)))
            with open(pdf_suser, "rb") as ufile:
                encoded_user = base64.b64encode(ufile.read())
        except:
            user_sign = Profile.objects.get(user=obj.user)
            user_sig = ''
            encoded_user = ''

        if obj.signer:
            signer = obj.signer
        else:
            signer = obj.user

        created_offer = obj.created.astimezone(pytz.timezone('CET'))

        l_years = []
        if obj.lissage:
            l_years = [int(y) for y in obj.years_liss_list]
        else:
            l_years = years

        ps1 = ParameterRecord.objects.filter(offer=obj, parameter=Parameter.objects.get(
            code='ps1')).values_list('value', flat=True)
        ps2 = ParameterRecord.objects.filter(offer=obj, parameter=Parameter.objects.get(
            code='ps2')).values_list('value', flat=True)
        exists_ps = sum(list(ps1)) != 0 and sum(list(ps2)) != 0
        # exists_ps2 = sum(list(ps2)) != 0

        if len(list(obj.address_pods)) > 7:
            eight_pod = list(obj.address_pods)[8]
        else:
            eight_pod = None

        average_year_price = BudgetAveragePerYearRiscs.objects.filter(
            budget__in=budgets, year__in=years).values('year', 'value')
        
        try:
            pdf_logo = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media/logo/logo_zeno.png')
            with open(pdf_logo, "rb") as lfile:
                encoded_logo = base64.b64encode(lfile.read())
        except:
            encoded_logo = ''
        

        context = {
            "url": url,
            "encoded_logo": encoded_logo,
            "encoded_admin": encoded_admin,
            "encoded_user": encoded_user,
            "budget_season": list(budget_season),
            "prices": list(average_year_price),
            "titles": len(list(obj.shedules.all().values_list('id', flat=True))),
            "years": years,
            "l_years": l_years,
            "customer": obj.company.name,
            "surname": obj.company.surname,
            "marche": obj.marche,
            "second_type": obj.second_type,
            "energy": obj.energyd,
            "energy_lower": obj.energyd.lower(),
            "grd": obj.grd,
            "offer": obj,
            "offer_from": offer_from,
            "year_sum": year_sum,
            "starpod": len(list(obj.address_pods)) > 7 and len(list(obj.address_pods)) != 8,
            "eight_pod": eight_pod,
            "spods": list(obj.address_pods)[:7],
            "pods": list(obj.address_pods)[:8],
            "all_pods": list(obj.address_pods)[8:],
            "len_pods": len(list(obj.address_pods)),
            "validation_time": str(expiration_date),
            "energies": list(energies),
            "len_years_list": len(obj.years_list),
            "fyear": fyear,
            "lyear": lyear,
            'signature': signature,
            'user_sign': user_sign,
            'admin_sig': admin_sig,
            'user_sig': user_sig,
            'signer': signer,
            'exists_ps': exists_ps,
            'identifier': '{}-{}_{}-{}-{}-{}-{}'.format(str(obj.company.nom_entrepise), str(obj.company.name), str(obj.company.surname), str(
                obj.years).replace(",", ""), str(obj.otype), obj.created.strftime("%d%m%Y"), str(obj.emp_id))
        }
        template = get_template('tool/mail/template.html')
        pdf_content = template.render(context)
        outputFilename = os.path.join(os.path.dirname(os.path.dirname(
            __file__)), 'media/offer-{}.pdf'.format(str(obj.id)))
        pdfkit.from_string(pdf_content, outputFilename)
        local_file = open(outputFilename, 'rb')
        # obj.unsigned_file.save('offer-{}.pdf'.format(str(obj.company.nom_entrepise)), File(local_file), save=True)
        obj.unsigned_file.save('{}-{}_{}-{}-{}-{}.pdf'.format(str(obj.company.nom_entrepise), str(obj.company.name), str(obj.company.surname), str(
            obj.years).replace(",", ""), str(obj.otype), created_offer.strftime("%d%m%Y-%H%M%S")), File(local_file), save=True)
        local_file.close()




    def get(self, request, pk, format=None):
        try:
            ip = request.META.get('HTTP_X_REAL_IP')
        except:
            ip = request.META.get('REMOTE_ADDR')
        print 'ip user = ', ip
        g = GeoIP2()
        country = ''
        city = ''
        latitude = 0
        longitude = 0
        # print g.city('109.185.174.82'), g.city('109.185.174.82')['latitude'], g.city('109.185.174.82')['longitude']
        if str(ip) != '127.0.0.1' and ip:
            try:
                print g.city(ip)
                if g.city(ip)['country_code'] == 'MD':
                    country = 'RO'
                    city = 'Iasi'
                    latitude = 47.1584549
                    longitude = 27.6014418
                else:
                    country = g.city(ip)['country_code']
                    city = g.city(ip)['city']
                    latitude = g.city(ip)['latitude']
                    longitude = g.city(ip)['longitude']
            except:
                country = ''
                city = ''
        cet = pytz.timezone('UTC')
        snippet = get_object_or_404(Offer, token=pk)
        print snippet
        if request.is_mobile or request.is_tablet or request.is_phone:
            device = 'mobile'
        else:
            device = 'desktop'
        cl = ClientLog(offer=snippet, client=snippet.company, ip=str(ip), device=device,
                       log_type='click', country=country, city=city, latitude=latitude, longitude=longitude)
        cl.save()
        print cl
        expire_date = snippet.expiration_date.replace(tzinfo=None)
        print expire_date.replace(hour=23, minute=59), datetime.utcnow()
        # if expire_date.replace(hour=23, minute=59) < datetime.utcnow():
        #     Offer.objects.filter(token=pk).update(token=None)
        #     return Response({'result':'Offer validation expired'}, status=status.HTTP_200_OK)
        serializer = OfferSerializer(snippet)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def post(self, request, pk, format=None):
        try:
            ip = request.META.get('HTTP_X_REAL_IP')
        except:
            ip = request.META.get('REMOTE_ADDR')
        print 'ip user = ', ip
        g = GeoIP2()
        country = ''
        city = ''
        latitude = 0
        longitude = 0
        # print g.city('109.185.174.82'), g.city('109.185.174.82')['latitude'], g.city('109.185.174.82')['longitude']
        if str(ip) != '127.0.0.1' and ip:
            try:
                print g.city(ip)
                if g.city(ip)['country_code'] == 'MD':
                    country = 'RO'
                    city = 'Iasi'
                    latitude = 47.1584549
                    longitude = 27.6014418
                else:
                    country = g.city(ip)['country_code']
                    city = g.city(ip)['city']
                    latitude = g.city(ip)['latitude']
                    longitude = g.city(ip)['longitude']
            except:
                country = ''
                city = ''
        if request.is_mobile or request.is_tablet or request.is_phone:
            device = 'mobile'
        else:
            device = 'desktop'
        
        try:
            obj = Offer.objects.get(token=pk)
        except:
            return Response({'result':'Offer not found'}, status=status.HTTP_400_BAD_REQUEST)
        print obj.token
        print request.data['accepted']
        
        if request.get_host() == '79.137.34.74':
            url = request.scheme + '://' + 'energysalesdirect.com:9090'
        else:
            url = request.scheme + '://' + request.get_host()
        
        try:
            if request.data['accepted'] == True:
                obj.offer_status = 'signer'
                obj.mail_date = None
                obj.save()
                self.render_email_pdf(obj, url)
                email_content = generate_email_content(obj, 'admin', url)
                print 'mail == ', obj.user.email
                TO = obj.user.email
                FROM = getattr(settings, 'MAIL_NAME')
                py_mail(obj.name, email_content, [], TO, FROM)
                cl = ClientLog(offer=obj, client=obj.company, ip=str(ip), device=device,
                               log_type='signer', country=country, city=city, latitude=latitude, longitude=longitude)
                cl.save()
                return Response({'result':'Email was send'}, status=status.HTTP_200_OK)
            else:
                cl = ClientLog(offer=obj, client=obj.company, ip=str(ip), device=device,
                               log_type='refuse', country=country, city=city, latitude=latitude, longitude=longitude)
                cl.save()
                return Response({'result':'Offer was no accepted'}, status=status.HTTP_200_OK)
        except:
            return Response({'result':'Offer has no accepted value'}, status=status.HTTP_400_BAD_REQUEST)



class OfferSendPdfMailByIdView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def generate_email_content(self, obj, url):
        if obj.offer_type == 'Standart':
            expiration_date = obj.expiration_date.replace(hour=23, minute=59).strftime('%d/%m/%Y %H:%M')
        else:
            interval_date_fin = pytz.utc.localize(datetime.strptime(str(obj.date_fin)[:16], '%Y-%m-%d %H:%M'))
            value = interval_date_fin.astimezone(pytz.timezone('CET'))
            expiration_date = value.strftime('%d/%m/%Y %H:%M')
        
        try:
            pdf_logo = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media/logo/logo_zeno.png')
            with open(pdf_logo, "rb") as lfile:
                encoded_logo = base64.b64encode(lfile.read())
        except:
            encoded_logo = ''

        context = {
                    "sex": obj.company.sex,
                    "customer": obj.company.name,
                    "surname": obj.company.surname,
                    "expiration_date": expiration_date,
                    "encoded_logo": encoded_logo,
                    "offer": obj,
                    "url": url,
                  }
        template = get_template('tool/mail/email-pdf.html')
        email_content = template.render(context)
        # print email_content
        return email_content


    def post(self, request, pk, format=None):
        if request.get_host() == '79.137.34.74':
            url = request.scheme + '://' + 'energysalesdirect.com:9090'
        else:
            url = request.scheme + '://' + request.get_host()
        
        try:
            ip = request.META.get('HTTP_X_REAL_IP')
        except:
            ip = request.META.get('REMOTE_ADDR')
        # TO = 'nicolae.botnaru@gmail.com'
        # FROM = 'non.commodity.data@gmail.com'
        # py_mail('Meta data', str(request.META), [], TO, FROM)
        # print 'ip user = ', ip, type(ip)
        g = GeoIP2()
        country = ''
        city = ''
        latitude = 0
        longitude = 0
        # print g.city('109.185.174.82'), g.city('109.185.174.82')['latitude'], g.city('109.185.174.82')['longitude']
        if str(ip) != '127.0.0.1' and ip:
            try:
                print g.city(ip)
                if g.city(ip)['country_code'] == 'MD':
                    country = 'RO'
                    city = 'Iasi'
                    latitude = 47.1584549
                    longitude = 27.6014418
                else:
                    country = g.city(ip)['country_code']
                    city = g.city(ip)['city']
                    latitude = g.city(ip)['latitude']
                    longitude = g.city(ip)['longitude']
            except:
                country = ''
                city = ''
        
        try:
            admin = User.objects.get(id=int(request.data['userId']))
        except:
            admin = None

        from django.core.mail import EmailMessage
        try:
            obj = Offer.objects.get(id=pk)
        except:
            return Response({'result':'Offer not found'}, status=status.HTTP_400_BAD_REQUEST)

        print 'try sent email data == ', Company.objects.get(id=obj.company.id).email
        email_content = self.generate_email_content(obj, url)
        # print('email content == ', email_content)
        TO = Company.objects.get(id=obj.company.id).email
        # FROM ='non.commodity.data@gmail.com'
        FROM = getattr(settings, 'MAIL_NAME')
        print obj.unsigned_file
        if request.is_mobile or request.is_tablet or request.is_phone:
            device = 'mobile'
        else:
            device = 'desktop'
        tz = pytz.timezone('Europe/Berlin')
        print 'times === ', obj.expiration_date.replace(hour=23, minute=59).replace(tzinfo=None), datetime.utcnow()
        print('identificator = ', str(obj.unsigned_file)[9:-4])
       
        # if obj.expiration_date.replace(hour=23, minute=59).replace(tzinfo=None) < datetime.utcnow():
        #     return Response({'result':'Offer validation expired'}, status=status.HTTP_200_OK)
        # else:

        Offer.objects.filter(id=obj.id).update(mail_date=datetime.now())
        cl = ClientLog(offer=obj, client=obj.company, ip=str(ip), log_type='send', device=device,
                        country=country, city=city, admin=admin, latitude=latitude, longitude=longitude)
        
        # print('identificator = ', str(obj.unsigned_file)[8:-3])
        # py_mail(obj.name, email_content, ['media/' + str(obj.unsigned_file).encode('utf8')], TO, FROM)
        emails = obj.emails_list + [str(TO)]
        for mail in emails:
            if mail != '':
                py_mail(obj.name, email_content, ['media/' + str(obj.unsigned_file)], str(mail), FROM)
        return Response({'result':'Email was send'}, status=status.HTTP_200_OK)



class OfferSendThanksMailByIdView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def generate_email_content(self, obj, url):
        
        try:
            pdf_logo = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media/logo/logo_zeno.png')
            with open(pdf_logo, "rb") as lfile:
                encoded_logo = base64.b64encode(lfile.read())
        except:
            encoded_logo = ''
        
        context = {
                    "customer": obj.company.name,
                    "surname": obj.company.surname,
                    "encoded_logo": encoded_logo,
                    "offer": obj,
                    "url": url,
                  }
        template = get_template('tool/mail/email-thanks.html')
        email_content = template.render(context)
        # print email_content
        return email_content


    def post(self, request, pk, format=None):
        if request.get_host() == '79.137.34.74':
            url = request.scheme + '://' + 'energysalesdirect.com:9090'
        else:
            url = request.scheme + '://' + request.get_host()

        try:
            obj = Offer.objects.get(id=pk)
        except:
            return Response({'result':'Offer not found'}, status=status.HTTP_400_BAD_REQUEST)

        print 'try sent email data == ', Company.objects.get(id=obj.company.id).email
        email_content = self.generate_email_content(obj, url)
        TO = Company.objects.get(id=obj.company.id).email
        FROM = getattr(settings, 'MAIL_NAME')
        Offer.objects.filter(id=obj.id).update(mail_date=datetime.now())
        emails = obj.emails_list + [str(TO)]
        for mail in emails:
            if mail != '':
                py_mail(obj.name, email_content, [], TO, FROM)
        return Response({'result':'Email was send'}, status=status.HTTP_200_OK)


class OfferByIdStatusView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def render_email_pdf(self, obj, url):
        cet = pytz.timezone('UTC')
        import pdfkit
        try:
            if obj.pfc_market:
                energys = RiscRecord.objects.filter(pfc_market=obj.pfc_market,
                                                    risc=Risc.objects.get(code=obj.energy_type)
                                                    ).values('year', 'value', 'risc')
            else:
                energys = RiscRecord.objects.filter(pfc=obj.pfc,
                                                    risc=Risc.objects.get(code=obj.energy_type)
                                                    ).values('year', 'value', 'risc')
        except:
            energies = []

        majors = ParameterRecord.objects.filter(
            offer=obj, parameter=Parameter.objects.get(code='sur_go')).values('year', 'value')

        # print 'energies === ', obj.pfc, energies
        # energys = defaultdict()
        energies = []

        for major in majors:
            for energy in energys:
                if int(energy['year']) == int(major['year']):
                    if major['value']:
                        # energys[str(energy['year'])] = energy['value'] + major['value']
                        energies.append({'year': energy['year'],
                                         'value': energy['value'] + major['value']})
                    else:
                        energies.append({'year': energy['year'], 'value': energy['value']})
                        # energys[str(energy['year'])] = energy['value']

        # print 'energies ===== ', energies

        energy_med = EnergyConsumptionRecord.objects.filter(meter=obj.cc).only(
            'interval_start', 'value').order_by('interval_start')

        meds = TranslationRecord.objects.filter(meter=obj.cc).only(
            'interval_start', 'value').order_by('interval_start')

        year_sum = defaultdict()

        for year in obj.years_list + [str(obj.cc.site.year)]:
            # data_from = cet.localize(datetime(int(year), 01, 01, 0, 0), is_dst=None)
            # data_to = cet.localize(datetime(int(year), 12, 31, 23, 59), is_dst=None)

            if obj.pfc_date_first:
                fdate = make_naive(obj.pfc_date_first, pytz.timezone('CET'))
                if fdate.year == int(year):
                    data_from = cet.localize(
                        datetime(int(year), fdate.month, fdate.day, 0, 0), is_dst=None)
                else:
                    data_from = cet.localize(datetime(int(year), 01, 01, 0, 0), is_dst=None)
            else:
                data_from = cet.localize(datetime(int(year), 01, 01, 0, 0), is_dst=None)

            if obj.pfc_date_last:
                ldate = make_naive(obj.pfc_date_last, pytz.timezone('CET'))
                if ldate.year == int(year):
                    data_to = cet.localize(datetime(int(year), ldate.month,
                                                    ldate.day, 23, 59), is_dst=None)
                else:
                    data_to = cet.localize(datetime(int(year), 12, 31, 23, 59), is_dst=None)
            else:
                data_to = cet.localize(datetime(int(year), 12, 31, 23, 59), is_dst=None)

            if str(year) == str(obj.cc.site.year):
                energ_sum = energy_med.filter(
                    interval_start__gte=data_from, interval_start__lte=data_to).aggregate(Sum('value'))
            else:
                energ_sum = meds.filter(interval_start__gte=data_from,
                                        interval_start__lte=data_to).aggregate(Sum('value'))
            # print(meds.filter(interval_start__gte=data_from, interval_start__lte=data_to))
            # print data_from, data_to

            # if energ_sum == None:
            #     energ_sum = energy_med.filter(interval_start__gte=data_from, interval_start__lte=data_to).aggregate(Sum('value'))

            year_sum[int(year)] = "{:,}".format(
                int(round(energ_sum['value__sum']))).replace(",", "'")

        # year_sum = {
        #     k: "{:,}".format(int(round(sum(x.value for x in g)))).replace(",", "'")
        #     for k, g in groupby(list(meds) + list(energy_med), key=lambda i: i.interval_start.year)
        # }
        # print year_sum
        print obj.meters
        if obj.offer_type == 'Standart':
            expiration_date = obj.expiration_date.replace(
                hour=23, minute=59).strftime('%d.%m.%Y %H:%M')
        else:
            # cet = pytz.timezone('UTC')
            interval_date_fin = pytz.utc.localize(datetime.strptime(
                str(obj.date_fin)[:16], '%Y-%m-%d %H:%M'))
            value = interval_date_fin.astimezone(pytz.timezone('CET'))
            expiration_date = value.strftime('%d.%m.%Y %H:%M')

        if obj.pfc_market:
            budgets = Budget.objects.filter(
                offer_id=obj.id, pfc_market=obj.pfc_market).values_list('id', flat=True)
            years = Budget.objects.filter(
                offer_id=obj.id, pfc_market=obj.pfc_market).values_list('year', flat=True)
        else:
            budgets = Budget.objects.filter(
                offer_id=obj.id, pfc=obj.pfc).values_list('id', flat=True)
            years = Budget.objects.filter(
                offer_id=obj.id, pfc=obj.pfc).values_list('year', flat=True)

        years = sorted(reduce(lambda r, v: v in r and r or r + [v], years, []))
        budget_season = BudgetMedSeasonWithRiscsRecord.objects.filter(budget__in=budgets,
                                                                      year__in=years).annotate(hp_hc=F('schedule__title')).values('year', 'value', 'season', 'hp_hc')
        title_ids = BudgetMedSeasonRecord.objects.filter(budget__in=budgets, year__in=years).annotate(
            hp_hc_id=F('schedule__id')).values_list('hp_hc_id', flat=True)
        title_ids = sorted(reduce(lambda r, v: v in r and r or r + [v], title_ids, []))
        print 'lenght == ', len(list(title_ids))
        fyear = obj.years_list[0]
        lyear = obj.years_list[-1]
        offer_from = datetime(int(fyear), 01, 01, 0, 0)
        try:
            signature = Profile.objects.get(user=obj.signer)
            admin_sig = signature.signature
            
            pdf_sadmin = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media/{}'.format(str(admin_sig)))
            with open(pdf_sadmin, "rb") as sfile:
                encoded_admin = base64.b64encode(sfile.read())
        except:
            signature = Profile.objects.get(user=obj.user)
            admin_sig = ''
            encoded_admin = ''

        try:
            user_sign = Profile.objects.get(user=obj.user)
            user_sig = user_sign.signature
            pdf_suser = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media/{}'.format(str(user_sig)))
            with open(pdf_suser, "rb") as ufile:
                encoded_user = base64.b64encode(ufile.read())
        except:
            user_sign = Profile.objects.get(user=obj.user)
            user_sig = ''
            encoded_user = ''

        if obj.signer:
            signer = obj.signer
        else:
            signer = obj.user

        created_offer = obj.created.astimezone(pytz.timezone('CET'))

        l_years = []
        if obj.lissage:
            l_years = [int(y) for y in obj.years_liss_list]
        else:
            l_years = years

        ps1 = ParameterRecord.objects.filter(offer=obj, parameter=Parameter.objects.get(
            code='ps1')).values_list('value', flat=True)
        ps2 = ParameterRecord.objects.filter(offer=obj, parameter=Parameter.objects.get(
            code='ps2')).values_list('value', flat=True)
        exists_ps = sum(list(ps1)) != 0 and sum(list(ps2)) != 0
        # exists_ps2 = sum(list(ps2)) != 0

        if len(list(obj.address_pods)) > 7:
            eight_pod = list(obj.address_pods)[8]
        else:
            eight_pod = None

        average_year_price = BudgetAveragePerYearRiscs.objects.filter(budget__in=budgets, year__in=years).values('year', 'value')

        # pdf_logo = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media/offer-{}.pdf'.format(str(obj.id)))
        try:
            pdf_logo = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media/logo/logo_zeno.png')
            with open(pdf_logo, "rb") as lfile:
                encoded_logo = base64.b64encode(lfile.read())
        except:
            encoded_logo = ''
        
        context = {
            "url": url,
            "encoded_logo": encoded_logo,
            "encoded_admin": encoded_admin,
            "encoded_user": encoded_user,
            "budget_season": list(budget_season),
            "prices": list(average_year_price),
            "titles": len(list(obj.shedules.all().values_list('id', flat=True))),
            "years": years,
            "l_years": l_years,
            "customer": obj.company.name,
            "surname": obj.company.surname,
            "marche": obj.marche,
            "second_type": obj.second_type,
            "energy": obj.energyd,
            "energy_lower": obj.energyd.lower(),
            "grd": obj.grd,
            "offer": obj,
            "offer_from": offer_from,
            "year_sum": year_sum,
            "starpod": len(list(obj.address_pods)) > 7 and len(list(obj.address_pods)) != 8,
            "eight_pod": eight_pod,
            "spods": list(obj.address_pods)[:7],
            "pods": list(obj.address_pods)[:8],
            "all_pods": list(obj.address_pods)[8:],
            "len_pods": len(list(obj.address_pods)),
            "validation_time": str(expiration_date),
            "energies": list(energies),
            "len_years_list": len(obj.years_list),
            "fyear": fyear,
            "lyear": lyear,
            'signature': signature,
            'user_sign': user_sign,
            'admin_sig': admin_sig,
            'user_sig': user_sig,
            'signer': signer,
            'exists_ps': exists_ps,
            'identifier': '{}-{}_{}-{}-{}-{}-{}'.format(str(obj.company.nom_entrepise), str(obj.company.name), str(obj.company.surname), str(
                obj.years).replace(",", ""), str(obj.otype), obj.created.strftime("%d%m%Y"), str(obj.emp_id))
        }
        template = get_template('tool/mail/template.html')
        # pdf_content = 'context'
        pdf_content = template.render(context)
        outputFilename = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media/offer-{}.pdf'.format(str(obj.id)))
        pdfkit.from_string(pdf_content, outputFilename)
        local_file = open(outputFilename, 'rb')
        # obj.unsigned_file.save('offer-{}.pdf'.format(str(obj.company.nom_entrepise)), File(local_file), save=True)
        obj.unsigned_file.save('{}-{}_{}-{}-{}-{}.pdf'.format(str(obj.company.nom_entrepise), str(obj.company.name), str(obj.company.surname), str(
            obj.years).replace(",", ""), str(obj.otype), created_offer.strftime("%d%m%Y-%H%M%S")), File(local_file), save=True)
        local_file.close()

    def put(self, request, pk, format=None):
        try:
            ip = request.META.get('HTTP_X_REAL_IP')
        except:
            ip = request.META.get('REMOTE_ADDR')

        g = GeoIP2()
        country = ''
        city = ''
        latitude = 0
        longitude = 0
        # print g.city('109.185.174.82'), g.city('109.185.174.82')['latitude'], g.city('109.185.174.82')['longitude']
        if str(ip) != '127.0.0.1' and ip:
            try:
                print g.city(ip)
                if g.city(ip)['country_code'] == 'MD':
                    country = 'RO'
                    city = 'Iasi'
                    latitude = 47.1584549
                    longitude = 27.6014418
                else:
                    country = g.city(ip)['country_code']
                    city = g.city(ip)['city']
                    latitude = g.city(ip)['latitude']
                    longitude = g.city(ip)['longitude']
            except:
                country = ''
                city = ''
        try:
            admin = User.objects.get(id=int(request.data['id']))
        except:
            admin = None

        if request.get_host() == '79.137.34.74':
            url = request.scheme + '://' + 'energysalesdirect.com:9090'
        else:
            url = request.scheme + '://' + request.get_host()

        snippet = get_object_or_404(Offer, pk=pk)
        snippet.signee_date = None
        snippet.mail_date = None
        snippet.save()

        if snippet.lissage == True and snippet.offer_status == 'signee':
            return Response(status=status.HTTP_200_OK)
        serializer = OfferEditStatusSerializer(snippet, data=request.data)
        if request.data['statusDo'] == 'confirmer':
            # offers = Offer.objects.filter(cc=snippet.cc, lissage=snippet.lissage).exclude(
            #     id=snippet.id).exclude(offer_status='confirmer').exclude(offer_status='indicative')
            offers = []
        else:
            if request.data['offer_status'] == 'indicative':
                offers = []
            else:
                offers = Offer.objects.filter(cc=snippet.cc, lissage=snippet.lissage).exclude(
                    id=snippet.id).exclude(offer_status='confirmer')
        print offers
        if request.is_mobile or request.is_tablet or request.is_phone:
            device = 'mobile'
        else:
            device = 'desktop'
        loffers = []
        for offer in offers:
            for year in snippet.years.split(','):
                if year in offer.years.split(','):
                    loffers.append(offer.id)
        if request.data['offer_status'] != 'supprimer':
            Offer.objects.filter(id__in=loffers).update(offer_status='supprimer')
        # if request.data['offer_status'] == 'indicative' or request.data['offer_status'] == 'supprimer':
        #     snippet.signed_file = None
        #     snippet.unsigned_file = None
        #     snippet.eligibilite = None
        if request.data['offer_status'] == 'signee':
            cl = ClientLog(offer=snippet, client=snippet.company, ip=str(ip), device=device,
                           log_type='signee', country=country, city=city, admin=admin, latitude=latitude, longitude=longitude)
            cl.save()
            # snippet.unsigned_file = None
            snippet.signee_date = datetime.now()
            snippet.save()
        if request.data['offer_status'] == 'signer':
            cl = ClientLog(offer=snippet, client=snippet.company, ip=str(ip), device=device,
                           log_type='signer', country=country, city=city, admin=admin, latitude=latitude, longitude=longitude)
            cl.save()
            self.render_email_pdf(snippet, url)
        if request.data['statusDo'] == 'confirmer':
            cl = ClientLog(offer=snippet, client=snippet.company, ip=str(ip), device=device,
                           log_type='created', country=country, city=city, admin=admin, latitude=latitude, longitude=longitude)
            cl.save()
            snippet.signer = User.objects.get(id=int(request.data['id']))
            snippet.save()
            email_content = generate_email_content(snippet, 'confirmer', url)
            # TO = Company.objects.get(id=snippet.company.id).email
            # FROM = 'non.commodity.data@gmail.com'
            TO = snippet.user.email
            FROM = getattr(settings, 'MAIL_NAME')
            py_mail(snippet.name, email_content, [], TO, FROM)

        if request.data['statusDo'] == 'signer' and request.data['offer_status'] == 'supprimer' and snippet.lissage == True:
            snippet.offer_status = request.data['offer_status']
            snippet.save()
            try:
                ofr = Offer.objects.get(int(id=snippet.lissage_base))
                ofr.status_lisse = False
                ofr.save()
            except:
                print('no offer')

        if request.data['offer_status'] == 'supprimer' and snippet.lissage == True:
            snippet.offer_status = request.data['offer_status']
            snippet.save()
            try:
                ofr = Offer.objects.get(int(id=snippet.lissage_base))
                if ofr.lis_force == True:
                    ofr.lis_manual_expire = datetime.now() - timedelta(days=1)
                    ofr.save()
            except:
                print('no offer')

        if request.data['statusDo'] == 'signee' and snippet.lissage == True:
            snippet.offer_status = request.data['offer_status']
            snippet.signee_date = datetime.now()
            snippet.save()
            try:
                off = Offer.objects.get(int(id=snippet.lissage_base))
                off.status_lisse = False
                off.save()
            except:
                print('no offer')

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OfferByIdPfcView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk, format=None):
        snippet = get_object_or_404(Offer, pk=pk)
        try:
            pfc = PFC.objects.get(pfc_id=str(request.data['pfc']))
            request.data['pfc'] = pfc.id
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = OfferPfcEditSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_400_BAD_REQUEST)



class OfferByIdPfcMarketView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk, format=None):
        snippet = get_object_or_404(Offer, pk=pk)
        try:
            pfc = PFCMarket.objects.get(pfc_id=str(request.data['pfc']))
            request.data['pfc'] = pfc.id
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = OfferPfcEditSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class OfferByIdSignedYearsView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk, format=None):
        snippet = get_object_or_404(Offer, pk=pk)
        try:
            if request.data['signed_years'] != ['']:
                request.data['signed_years'] = ','.join(str(year) for year in request.data['signed_years'])
        except:
            return Response({'result':'No signed years found'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = OfferSignedEditSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class RiscsViewListSet(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        snippets = Risc.objects.all()
        serializer = RiscSerializer(snippets, context={"request": request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RiscsRecordViewListSet(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        snippets = RiscRecord.objects.all()
        serializer = RiscRecordSerializer(snippets, context={"request": request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # def post(self, request, format=None):
    #
    #     serializer = RiscRecordSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConstantsView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        snippets = Constants.objects.all()
        serializer = ConstantSerializer(snippets, context={"request": request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, format=None):
        print request.data
        try:
            for constant in request.data:
                snippet = get_object_or_404(Constants, id=constant['id'])
                print snippet
                serializer = ConstantSerializer(snippet, data=constant)
                print 'serializer= ', serializer
                if serializer.is_valid():
                    print 'true == ', serializer.is_valid()
                    serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GRDViewListSet(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        snippets = GRD.objects.all().order_by('pk')
        serializer = GRDSerializer(snippets, context={"request": request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GRDByIdViewSet(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        snippet = get_object_or_404(GRD, id=pk)
        serializer = GRDSerializer(snippet)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OfferSigneViewListSet(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        print request.data
        if request.data['offerId']:
            try:
                obj = Offer.objects.get(id=int(request.data['offerId']))
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        if request.FILES.getlist('files') == []:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        for f in request.FILES.getlist('files'):
            obj.signed_file.save('offer-signed-{}.pdf'.format(str(obj.id)), File(f), save=True)
        return Response({'received data': len(request.data)}, status=status.HTTP_201_CREATED)


class OfferEligibiliteViewListSet(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        print request.data
        if request.data['offerId']:
            try:
                obj = Offer.objects.get(id=int(request.data['offerId']))
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        if request.FILES.getlist('files') == []:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        for f in request.FILES.getlist('files'):
            obj.eligibilite.save('offer-eligibilite-{}.pdf'.format(str(obj.id)), File(f), save=True)
        return Response({'received data': len(request.data)}, status=status.HTTP_201_CREATED)


class OfferInsertMailSet(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        try:
            offer = Offer.objects.get(id=int(request.data['id']))
            emails = request.data['email']['mailRows']
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        saved_emails = ''
        for email in emails:
            saved_emails += email['mailname'] + ','
        offer.emails = saved_emails[:-1]
        offer.save()
        return Response({'received data': len(request.data)}, status=status.HTTP_201_CREATED)


class OfferExternViewListSet(APIView):
    # authentication_classes = (JSONWebTokenAuthentication, )
    # permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        if request.get_host() == '79.137.34.74':
            return Response(status=status.HTTP_403_FORBIDDEN)
            
        dat_from = self.request.query_params.get('date_from', None)
        dat_to = self.request.query_params.get('date_to', None)

        q = Q()
        if dat_from and dat_to:
            date_from = datetime.strptime(dat_from, '%d.%m.%Y')
            date_to = datetime.strptime(dat_to, '%d.%m.%Y') + timedelta(days=1)
            q &= Q(created__gte=date_from, created__lte=date_to)

        snippets = Offer.objects.filter(offer_status__in=['signee', 'indicative', 'signer'], lis_force=False).filter(q)
        serializer = OfferTiagoSerializer(snippets, context={"request": request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OfferExternByIdView(APIView):
    # authentication_classes = (JSONWebTokenAuthentication, )
    # permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, pk, format=None):
        if request.get_host() == '79.137.34.74':
            return Response(status=status.HTTP_403_FORBIDDEN)
        snippet = get_object_or_404(Offer, id=pk)
        serializer = OfferExternSerializer(snippet)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OfferParametersByIdView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, pk, format=None):
        snippet = get_object_or_404(Offer, id=pk)
        parameters = ParameterRecord.objects.filter(offer=snippet).values('parameter__code', 'parameter__name', 'value', 'year')
        return Response({'parameters': parameters}, status=status.HTTP_200_OK)
