# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import *
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.utils import jwt_decode_handler
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, timedelta
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core import serializers
from django.conf import settings
from django.utils.timezone import get_current_timezone, make_aware, make_naive
from django.utils import timezone
from pytz import country_timezones
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpRequest
import json
import pytz
import os
import time
import csv
import requests
import StringIO
from contextlib import closing
from django.db import connection
from django.views.generic import View
from rest_framework import viewsets
from collections import defaultdict
from operator import itemgetter
from rest_framework import status
from offers.utils.send_mail import py_mail
from budget.models import *
from core.models import *
from client.models import *
from companies.models import *
from offers.models import *
from .models import *
from .forms import *
from .serializers import *
from offers.serializers import *
from .logic.db.upload import upload_pfc_db
from .logic.cockpit.check import new_data, update_data, update_market_data, get_last_pfc


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
        print 'weekend ========= ', weekend
        exp = datetime.utcnow() + timedelta(days=int(validation_time) + weekend)
        print 'exp ======= ', exp, 8-exp.isoweekday()
        if exp.isoweekday() > 5:
            return exp.replace(hour=23, minute=59) + timedelta(days=8-exp.isoweekday())
        else:
            return exp.replace(hour=23, minute=59)



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
                "year_sum": year_sum,
                "prices": list(average_year_price),
                "years":years,
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
                "url": url
              }
    print 'context === ', context
    template = get_template('tool/mail/email.html')
    email_content = template.render(context)
    # print email_content
    return email_content




class PFCFileViewSet(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        snippets = PfcConsumptionFile.objects.all()
        serializer = PfcConsumptionFileSerializer(snippets, context={"request": request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # def post(self, request, format=None):
    #     print request.data
    #     serializer = PfcConsumptionFileSerializer(data=request.data)
    #     # if serializer.is_valid():
    #         # serializer.save()
    #         # return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PFCViewSet(APIView):
    # authentication_classes = (JSONWebTokenAuthentication, )
    # permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        # pfc_data = new_data()
        # lpfc = update_data(pfc_data)
        
        snippets = PFC.objects.all()
        if not snippets:
            return Response([], status=status.HTTP_200_OK)
        reg_list = [{'id': pfc.id, 'pfc_id': datetime.strptime(pfc.pfc_id, '%d.%m.%Y'), 'created': pfc.created} for pfc in list(snippets)]
        records_list = sorted(reg_list, key=lambda x: x['pfc_id'], reverse=True)
        print(records_list)
        data_riscs = [{'id': pfc['id'], 'pfc_id':  pfc['pfc_id'].strftime('%d.%m.%Y'), 'created': pfc['created']} for pfc in records_list]
        # serializer = PFCSerializer(snippets, context={"request": request}, many=True)
        
        return Response(data_riscs, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = PFCSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PFCByIdView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)


    def get(self, request, pk, format=None):
        snippet = get_object_or_404(PFC, id=pk)
        serializer = PFCSerializer(snippet)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, pk, format=None):
        snippet = get_object_or_404(PFC, id=pk)
        serializer = PFCSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        snippet = get_object_or_404(PFC, id=pk)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PFCByDateView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)


    def get(self, request, format=None):
        date = self.request.query_params.get('date', None)
        if date == None or date == '':
            return Response({'pfc': 'No data'}, status=status.HTTP_404_NOT_FOUND)
        dat_str = datetime.strptime(date, '%d.%m.%Y')
        dat = dat_str.strftime('%d.%m.%Y')
        snippet = get_object_or_404(PFC, pfc_id=dat)
        serializer = PFCSerializer(snippet)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # def put(self, request, pk, format=None):
    #     snippet = get_object_or_404(PFC, id=pk)
    #     serializer = PFCSerializer(snippet, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #
    # def delete(self, request, pk, format=None):
    #     snippet = get_object_or_404(PFC, id=pk)
    #     snippet.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)


class PFCMarketByIdView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        snippet = get_object_or_404(PFCMarket, id=pk)
        serializer = PFCMarketSerializer(snippet)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        snippet = get_object_or_404(PFCMarket, id=pk)
        serializer = PFCMarketSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        snippet = get_object_or_404(PFCMarket, id=pk)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PFCMarketViewSet(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        snippets = PFCMarket.objects.all()
        serializer = PFCMarketSerializer(snippets, context={"request": request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = PFCMarketSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PfcRecordsByYearView(APIView):
    # authentication_classes = (JSONWebTokenAuthentication, )
    # permission_classes = (IsAuthenticated,)

    def get(self, request, year, format=None):
        unit = self.request.query_params.get('unit', None)
        pfc = self.request.query_params.get('pfc', None)
        q = Q()
        if unit:
            q &= Q(unit=str(unit))
        else:
            unit = 'CHF'
        cet = pytz.timezone('CET')
        # cet = pytz.timezone('UTC')
        pfc_from = cet.localize(datetime(int(year), 01, 01, 0, 0), is_dst=None)
        pfc_to = cet.localize(datetime(int(year), 12, 31, 23, 59), is_dst=None)
        cet_pfc_from = make_aware(pfc_from.replace(tzinfo=None), cet, is_dst=None)
        cet_pfc_to = make_aware(pfc_to.replace(tzinfo=None), cet, is_dst=None)
        dat_str = datetime.strptime(pfc, '%d.%m.%Y')
        pfc_id = dat_str.strftime('%d.%m.%Y')
        print pfc, pfc_id
        records = PfcConsumptionRecord.objects.filter(q).filter(pfc__pfc_id=pfc_id, interval_start__gte=cet_pfc_from,
                                                                interval_start__lte=cet_pfc_to).values_list('interval_start', 'value').order_by('interval_start')
        # print records

        if not records:
            return Response({'data': 'Pfc', 'records': []}, status=status.HTTP_404_NOT_FOUND)
        reg_list = [[f.astimezone(pytz.timezone('CET')), s] for [f, s] in records]
        records_list = sorted(reg_list, key=lambda x: x[0])
        # record_list = ['[Date.UTC('+str(f.year)+','+str(f.month)+','+str(f.day)+','+str(f.hour)+','+str(f.minute)+'),'+ str(s)+'],' for [f, s] in records_list]
        record_list = [[(f.replace(tzinfo=None) - datetime.utcfromtimestamp(0)
                         ).total_seconds() * 1000.0, s] for [f, s] in records_list]
        # record_string = '([\n'+'\n'.join(record_list)+']);'
        # d = len(record_string)
        # records_string = ''.join([record_string[i] for i in range(len(record_string)) if i  != d-4])
        print type(record_list)
        return Response({'data': 'Pfc', 'records': record_list}, status=status.HTTP_200_OK)

class PfcMarketRecordsByYearView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, year, format=None):
        unit = self.request.query_params.get('unit', None)
        pfc = self.request.query_params.get('pfc', None)
        q = Q()
        if unit:
            q &= Q(unit = str(unit))
        else:
            unit = 'CHF'
        # cet = pytz.timezone('CET')
        cet = pytz.timezone('UTC')
        pfc_from = cet.localize(datetime(int(year), 01, 01, 0, 0), is_dst=None)
        pfc_to = cet.localize(datetime(int(year), 12, 31, 23, 59), is_dst=None)
        cet_pfc_from = make_aware(pfc_from.replace(tzinfo=None), cet, is_dst=None)
        cet_pfc_to = make_aware(pfc_to.replace(tzinfo=None), cet, is_dst=None)
        records = PfcMarketConsumptionRecord.objects.filter(q).filter(pfc_market__pfc_id=pfc, interval_start__gte=cet_pfc_from, interval_start__lte=cet_pfc_to).values_list('interval_start', 'value').order_by('interval_start')
        print 'records', records
        if not records:
            return Response(status=status.HTTP_404_NOT_FOUND)
        reg_list = [[make_naive(f, cet), s] for [f, s] in records]
        records_list = sorted(reg_list, key=lambda x: x[0])
        record_list = [[(f - datetime.utcfromtimestamp(0)).total_seconds() * 1000.0, s] for [f, s] in records_list]
        # record_list = ['[Date.UTC('+str(f.year)+','+str(f.month)+','+str(f.day)+','+str(f.hour)+','+str(f.minute)+'),'+ str(s)+'],' for [f, s] in records_list]
        # record_string = '([\n'+'\n'.join(record_list)+']);'
        # d = len(record_string)
        # records_string = ''.join([record_string[i] for i in range(len(record_string)) if i  != d-4])
        return Response({'data': 'Pfc Market', 'records': record_list}, status=status.HTTP_200_OK)


class PfcRecordsUnitsView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        units = PfcConsumptionRecord.objects.all().values_list('unit', flat=True)
        if not units:
            return Response({'units': ['CHF']}, status=status.HTTP_200_OK)
        else:
            units = reduce(lambda r, v: v in r and r or r + [v], units, [])
        return Response({'units': units}, status=status.HTTP_200_OK)



#
# # Get last and first date for a period of pfcs
#
class PfcFirstRecordView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        pfc = self.request.query_params.get('pfc', None)
        years = self.request.query_params.get('years', None)
        year_list = []

        if years is not None:
          for year in years.split(','):
            year_list.append(int(year))
        
        all_data = []
        cet = pytz.timezone('CET')

        try:
            for dyear in year_list:
                data = PfcConsumptionRecord.objects.filter(pfc_id=int(pfc), interval_start__year=dyear).values_list('interval_start', flat=True).order_by('interval_start')
                reg_list = [make_naive(f, cet) for f in data]
                records_list = sorted(reg_list, key=lambda x: x)
                all_data = all_data + records_list
            
            all_data = sorted(all_data, key=lambda x: x)
            first_pfc = list(all_data)[0]
            last_pfc = list(all_data)[-1]
        except:
            first_pfc = None
            last_pfc = None
        # print({'first': str(first_pfc).replace("T", " "), 'last': str(last_pfc).replace("T", " ")})
        return Response({'first': str(first_pfc).replace("T", " "), 'last': str(last_pfc).replace("T", " ")}, status=status.HTTP_200_OK)



class PfcFilesUploadView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    parser_classes = (FormParser, MultiPartParser)
    def post(self, request, format=None):
        print request.data['pfc_market']
        print request.FILES.getlist('files')[0], type(request.FILES.getlist('files')[0])
        try:
            today = request.data['date']
            dat_str = datetime.strptime(today, '%d.%m.%Y')
            today = dat_str.strftime('%d.%m.%Y')
        except:
            today = datetime.now().strftime("%d.%m.%Y")
        if request.data['pfc_market'] == 'true':
            currentPfc = PFCMarket.objects.filter(pfc_id=today)
            # offer = Offer.object.get(id=request.data['offerId'])
            # offer.pfc_market = currentPfc
            # offer.save()
        else:
            currentPfc = PFC.objects.filter(pfc_id=today)
        if currentPfc:
            currentPfc[0].pfc_id = currentPfc[0].pfc_id + ' ' + str(currentPfc[0].time)
            currentPfc[0].time = None
            currentPfc[0].save()
        print 'currentPfc === ', currentPfc
        time = datetime.now().time()
        print 'time = ', str(time)[:5]
        # print request.FILES.getlist('files')
        if request.data['pfc_market'] == 'true':
            pfc = PFCMarket.objects.create(pfc_id = today, time=' ' + str(time))
        else:
            pfc = PFC.objects.create(pfc_id = today, time=' ' + str(time)[:5])
        if request.FILES.getlist('files') == []:
            return Response({'Error': 'Missing files'}, status=status.HTTP_404_NOT_FOUND)
        
        CONTENT_TYPES = ['.xlsx', '.xls']

        for f in request.FILES.getlist('files'):
            filename, file_extension = os.path.splitext(f.name)
            if file_extension not in CONTENT_TYPES:
                return Response({'Error': 'File bad format'}, status=status.HTTP_400_BAD_REQUEST)
            if request.data['pfc_market'] == 'true':
                instance = PfcConsumptionFile(data_file = f, pfc_market = pfc)
            else:
                instance = PfcConsumptionFile(data_file = f, pfc = pfc)
            instance.save()
        return Response({'received data': len(request.data), 'pfc': pfc.id}, status=status.HTTP_201_CREATED)


class PfcAPIUploadView(APIView):
    # authentication_classes = (JSONWebTokenAuthentication, )
    # permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        
        pfc = update_data(request.data)

        today = datetime.now().date()
        cockpit_weekday_offers = CockpitOffer.objects.filter(cockpit_id=2, weekday__day=today.isoweekday()).values_list('offer', flat=True)
        print 'cockpit at the specific day of the week =', cockpit_weekday_offers

        from collections import defaultdict
        data_years = defaultdict()
        cockpits_offer = []

        today = datetime.now().date()
        if today.isoweekday() == 1:
            yesterday = today - timedelta(days=3)
        else:
            yesterday = today - timedelta(days=1)
        
        print 'today = ', today, today.replace(day=1)
        
        # cockpit at the start of the month
        if today == today.replace(day=1):
            month_cockpit = CockpitOffer.objects.filter(cockpit_id=3).values_list('offer', flat=True)
        else:
            month_cockpit = []
        print 'cockpit at the start of the month = ', month_cockpit
        
        # cockpit at the specific change in price
        cockpit_year_offers = CockpitOffer.objects.filter(cockpit_id=1)
        for ckof in cockpit_year_offers:
            if ckof.offer.pfc_market:
                budgets = Budget.objects.filter(offer=ckof.offer, pfc_market=ckof.offer.pfc_market).values_list('id', flat=True)
            else:
                budgets = Budget.objects.filter(offer=ckof.offer, pfc=ckof.offer.pfc).values_list('id', flat=True)
            years = ckof.offer.years.split(',')
            years = map(lambda x: int(x), years)
            year_sum = defaultdict()
            price_final = BudgetAveragePerYearRiscs.objects.filter(budget__in=budgets, year__in=years).values('year', 'value')
            for price in price_final:
                year_sum[price['year']] = price['value']

            # print 'each cockpit', (year_sum[int(ckof.year)] / float(year_nr[int(ckof.year)])) , ckof.lowest , (year_sum[int(ckof.year)] / float(year_nr[int(ckof.year)])) , ckof.highest
            if today >= ckof.date_from and today <= ckof.date_to:
                if year_sum[int(ckof.year)] < ckof.lowest or year_sum[int(ckof.year)] > ckof.highest:
                    cockpits_offer.append(ckof.offer.id)
        
        cockpits_offer = list(set(cockpits_offer))
        print 'cockpit at the specific change in price = ', cockpits_offer

        offerse = Offer.objects.filter(offer_status='indicative', offer_type='Standart', expiration_date__date=yesterday).values_list('id', flat=True)
        print 'offers expirate ===== ', offerse

        cockpit_offers = list(cockpit_weekday_offers) + list(month_cockpit) + list(cockpits_offer)
        offers = list(cockpit_weekday_offers) + list(month_cockpit) + list(cockpits_offer) + list(offerse)
        offers = list(set(offers))
        
        # offers = Offer.objects.filter(offer_status='indicative', offer_type='Standart', expiration_date__date=today)
        print 'offers toate ===== ', offers
        url = request.scheme + '://' + request.get_host()
        if offers:
            for offr in offers:
                offer = Offer.objects.get(id=int(offr))
                if offer.pfc != pfc:
                    odata = {
                        'id': offer,
                        'pfc': pfc.id
                    }
                    offer.expiration_date = expiration_date(offer.validation_time)
                    serializer = OfferPfcEditSerializer(offer, data=odata)
                    print('valid = ', offer, serializer.is_valid())
                    if serializer.is_valid():
                        serializer.save()
                        print('offr == ', offr)
                        email_content = generate_email_content(offer, 'client', url)
                        TO = Company.objects.get(id=offer.company.id).email
                        # FROM = 'non.commodity.data@gmail.com'
                        FROM = getattr(settings, 'MAIL_NAME')
                        py_mail(offer.name, email_content, [], TO, FROM)

        return Response({'received data': len(request.data)}, status=status.HTTP_201_CREATED)


class PfcAPIUpdatePermissionView(APIView):
    # authentication_classes = (JSONWebTokenAuthentication, )
    # permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        snippets = PFC.objects.all().exclude(time=None).exclude(time='')
        if not snippets:
            snippets = []
        reg_list = [{'id': pfc.id, 'pfc_id': datetime.strptime(pfc.pfc_id, '%d.%m.%Y'), 'created': pfc.created} for pfc in list(snippets)]
        records_list = sorted(reg_list, key=lambda x: x['pfc_id'], reverse=True)
        
        pfc = PFC.objects.get(id=records_list[0]['id'])

        today = datetime.now().date()
        cockpit_weekday_offers = CockpitOffer.objects.filter(cockpit_id=2, weekday__day=today.isoweekday()).values_list('offer', flat=True)
        print 'cockpit at the specific day of the week =', cockpit_weekday_offers

        from collections import defaultdict
        data_years = defaultdict()
        cockpits_offer = []

        today = datetime.now().date()
        
        if today.isoweekday() == 1:
            yesterday = today - timedelta(days=3)
        else:
            yesterday = today - timedelta(days=1)
        
        print 'today = ', today, today.replace(day=1)
        
        # cockpit at the start of the month
        if today == today.replace(day=1):
            month_cockpit = CockpitOffer.objects.filter(cockpit_id=3).values_list('offer', flat=True)
        else:
            month_cockpit = []
        print 'cockpit at the start of the month = ', month_cockpit
        
        # cockpit at the specific change in price
        cockpit_year_offers = CockpitOffer.objects.filter(cockpit_id=1)
        for ckof in cockpit_year_offers:
            if ckof.offer.pfc_market:
                budgets = Budget.objects.filter(offer=ckof.offer, pfc_market=ckof.offer.pfc_market).values_list('id', flat=True)
            else:
                budgets = Budget.objects.filter(offer=ckof.offer, pfc=ckof.offer.pfc).values_list('id', flat=True)
            years = ckof.offer.years.split(',')
            years = map(lambda x: int(x), years)
            year_sum = defaultdict()
            price_final = BudgetAveragePerYearRiscs.objects.filter(budget__in=budgets, year__in=years).values('year', 'value')
            for price in price_final:
                year_sum[price['year']] = price['value']

            if today >= ckof.date_from and today <= ckof.date_to:
                if year_sum[int(ckof.year)] < ckof.lowest or year_sum[int(ckof.year)] > ckof.highest:
                    cockpits_offer.append(ckof.offer.id)
        
        offers = Offer.objects.filter(offer_status='indicative', offer_type='Standart', expiration_date__date=yesterday).values_list('id', flat=True)
        print 'offers ===== ', offers

        offers = list(cockpit_weekday_offers) + list(month_cockpit) + list(cockpits_offer) + list(offers)
        offers = list(set(offers))

        if offers:
            for offr in offers:
                offer = Offer.objects.get(id=int(offr))
                if offer.pfc != pfc:
                    odata = {
                        'id': offer.id,
                        'pfc': pfc.id
                    }
                    offer.expiration_date = expiration_date(offer.validation_time)
                    serializer = OfferPfcEditSerializer(offer, data=odata)
                    # print 'valid = ', offer, serializer.is_valid()
                    if serializer.is_valid():
                        serializer.save()
                        print(offr)
                        email_content = generate_email_content(offer, 'client', url)
                        TO = Company.objects.get(id=offer.company.id).email
                        # FROM = 'non.commodity.data@gmail.com'
                        FROM = getattr(settings, 'MAIL_NAME')
                        py_mail(offer.name, email_content, [], TO, FROM)

        return Response({'received data': len(request.data)}, status=status.HTTP_201_CREATED)



class PfcSmeOportunitiesTodayView(APIView):
    # authentication_classes = (JSONWebTokenAuthentication, )
    # permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        today = datetime.now().date()
        nr_opportunites = Offer.objects.filter(offer_status='pending', offer_type='SME', date_debut__date=today).values_list('nr_opportunite', 'emp_id')
        # print 'offers nr_opportunites ===== ', nr_opportunites
        return Response({'nr_opportunites': list(nr_opportunites)}, status=status.HTTP_200_OK)


class PfcSmeCockpitView(APIView):
    # authentication_classes = (JSONWebTokenAuthentication, )
    # permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        
        url = request.scheme + '://' + request.get_host()
        ip = 'None'
        country = ''
        city = ''
        latitude = 0
        longitude = 0
        device = 'desktop'

        for opportunite, data in request.data['offers'].iteritems():
            if data['risqs'] and data['eco'] and data['pfc']:
                print('opportunite = ', opportunite)
                pfc_market = update_market_data(opportunite, data)
                print('pfcmmarket = ', pfc_market)
                # try:
                offer = Offer.objects.get(nr_opportunite=opportunite, emp_id=int(data['oid']))
                print('offer opportunite = ', offer)
                if offer.pfc_market != pfc_market:
                    odata = {
                        'id': offer.id,
                        'pfc_market': pfc_market.id
                    }
                    print(odata)
                    # offer.expiration_date = expiration_date(offer.validation_time)
                    serializer = OfferPfcMEditSerializer(offer, data=odata)
                    print 'valid = ', offer, serializer.is_valid()
                    if serializer.is_valid():
                        serializer.save()
                        cl = ClientLog(offer=offer, client=offer.company, ip=str(ip), log_type='aconfirmer',
                                    country=country, city=city, admin=offer.user, latitude=latitude, longitude=longitude, device=device)
                        cl.save()
                        if offer.fonction == 3:
                            email_content = generate_email_content(offer, 'confirmer', url)
                            TO = offer.user.email
                            FROM = getattr(settings, 'MAIL_NAME')
                            py_mail(offer.name, email_content, [], TO, FROM)
                        else:
                            for sign in offer.signatures.all():
                                email_content = generate_email_content(offer, 'fonction', url, sign)
                                TO = sign.email
                                # FROM = 'non.commodity.data@gmail.com'
                                FROM = getattr(settings, 'MAIL_NAME')
                                py_mail(offer.name, email_content, [], TO, FROM)
            # except:
            # print('Error')
        return Response(status=status.HTTP_200_OK)



class PfcRiscsByYearView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        year = self.request.query_params.get('year', '')
        market = self.request.query_params.get('market', 'false')
        q = Q()
        if year:
            q &= Q(year = int(year))
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
        from collections import defaultdict
        data_riscs = defaultdict(list)
        riscs = Risc.objects.all()
        print riscs
        pfcs = PFC.objects.all().exclude(time=None).exclude(time='').values_list('pfc_id', flat=True).order_by('-pk')[:20]
        pfcids = PFC.objects.all().exclude(time=None).exclude(time='').values_list('id', flat=True)
        pfcs_len = len(pfcs)
        rids = RiscRecord.objects.filter(pfc=None).values_list('rid', flat=True).exclude(rid=None)
        rids = list(set(rids))
        final_rids = l = list(set(rids) - set(pfcs))
        # pfcs_table = map(lambda dat: datetime.strftime(
        #     datetime.strptime(dat, '%d.%m.%Y'), "%d/%m/%y"), pfcs)
        pfcs = map(lambda dat: datetime.strftime(datetime.strptime(dat, '%d.%m.%Y'), "%Y-%m-%d"), pfcs)
        # try:
        # except:
        #     pfcs = []
        #     pfcs_len = 0
        for risc in riscs:
            if market.lower() == 'true':
                records = RiscRecord.objects.filter(q, pfc_id__in=pfcids, risc=risc).values_list('pfc_market__pfc_id', 'value').exclude(pfc_market=None)
                if records:
                    reg_list = [[datetime.strptime(f, '%d.%m.%Y'), s] for (f, s) in list(records)]
                    records_list = sorted(reg_list, key=lambda x: x[0])
                    data_riscs[risc.name] = [[f.date(), s] for [f, s] in records_list]
            elif market.lower() == 'false':
                records = RiscRecord.objects.filter(q, pfc_id__in=pfcids, risc=risc).values_list('pfc__pfc_id', 'value').exclude(pfc=None)
                if records:
                    rid_records = RiscRecord.objects.filter(q, pfc=None, rid__in=final_rids, risc=risc).values_list('rid', 'value').exclude(rid=None)
                    if rid_records:
                        records = records + rid_records
                    reg_list = [[datetime.strptime(f, '%d.%m.%Y'), s] for (f, s) in list(records)]
                    records_list = sorted(reg_list, key=lambda x: x[0])
                    data_riscs[risc.name] = [[f.date(), s] for [f, s] in records_list]
            else:
                records = []
        if not data_riscs:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response({'records': data_riscs, 'pfcs': pfcs, 'pfcs_len': pfcs_len}, status=status.HTTP_200_OK)



class UpdateCockpitSpecialView(APIView):
    # authentication_classes = (JSONWebTokenAuthentication, )
    # permission_classes = (IsAuthenticated,)

    def generate_cockpit_mail(self, pfc, years, pfc_id, hour, url):
        cet = pytz.timezone('UTC')
        import base64
        base_data = list(PfcPeakRecord.objects.filter(pfc=pfc, peak='base').values('year', 'value', 'peak'))
        peak_data = list(PfcPeakRecord.objects.filter(pfc=pfc, peak='peak').values('year', 'value', 'peak'))

        try:
            pdf_logo = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media/logo/romande-energie.png')
            with open(pdf_logo, "rb") as lfile:
                encoded_logo = base64.b64encode(lfile.read())
        except:
            encoded_logo = ''

        context = {
            "pfc": pfc,
            "pfc_id": pfc_id + ' ' + hour,
            "years": years,
            "base_data": base_data,
            "peak_data": peak_data,
            "encoded_logo": encoded_logo,
            "url": url,
        }

        template = get_template('tool/mail/email-cockpit.html')
        email_content = template.render(context)
        # print email_content
        return email_content

    def get(self, request, format=None):
        # pfc_id = self.request.query_params.get('day', '')
        # hour = self.request.query_params.get('hour', '')

        url = request.scheme + '://' + request.get_host()
        
        pfc = get_last_pfc()

        
        if PfcPeakRecord.objects.filter(pfc=pfc).exists():
            return Response({'result': 'already sent'}, status=status.HTTP_404_NOT_FOUND)
        
        records = PfcConsumptionRecord.objects.filter(pfc=pfc).order_by('interval_start')
        year_nr = {
            k: len(list(g))
            for k, g in groupby(records, key=lambda i: i.interval_start.year)
        }
        year_sum = {
            k: sum(x.value for x in g)
            for k, g in groupby(records, key=lambda i: i.interval_start.year)
        }

        for year, value in year_sum.iteritems():
            print(year, year_sum[year]/year_nr[year])
            pfcb = PfcPeakRecord(year=int(year), value=float(year_sum[year]/float(year_nr[year])), pfc=pfc, peak='base')
            pfcb.save()
        
        avg = defaultdict(list)
        for year in year_sum:
            cet = pytz.timezone('UTC')
            pfc_from = cet.localize(datetime(int(year), 01, 01, 0, 0), is_dst=None)
            pfc_to = cet.localize(datetime(int(year), 12, 31, 23, 00), is_dst=None)
            cet_pfc_from = make_aware(pfc_from.replace(tzinfo=None), cet, is_dst=None)
            cet_pfc_to = make_aware(pfc_to.replace(tzinfo=None), cet, is_dst=None)
            
            recs = records.filter(interval_start__gte = cet_pfc_from, interval_start__lte = cet_pfc_to).order_by('interval_start')
            # print recs
            for pfcr in recs:
                pfc_date = make_naive(pfcr.interval_start, pytz.timezone('utc'))
                if pfc_date.weekday() in [0, 1, 2, 3, 4] and pfc_date.hour in range(8, 20):
                    # print('pfc_date', pfc_date)
                    avg[year].append(pfcr.value)

        years = []
        for year in year_sum:
            years.append(int(year))
            print year, sum(avg[year])/len(avg[year])
            pfcp = PfcPeakRecord(year=int(year), value=sum(avg[year])/float(len(avg[year])), pfc=pfc, peak='peak')
            pfcp.save()

        email_content = self.generate_cockpit_mail(pfc, years, pfc.pfc_id, pfc.time, url)
        FROM = getattr(settings, 'MAIL_NAME')
        emails = []
        semails = list(SmeEmail.objects.all().values_list('email', flat=True))

        if str(request.get_host()) == str('10.4.4.72') or str(request.get_host()) == str('s1empprddb.pegase.lan'):
            emails = ['v.diaconu@energymarketprice.com', 'n.botnaru@energymarketprice.com'] + semails
        elif str(request.get_host()) == str('localhost:8000'):
            emails = ['n.botnaru@energymarketprice.com'] + semails
        else:
            emails = ['v.diaconu@energymarketprice.com', 'n.botnaru@energymarketprice.com'] + semails
        for TO in emails:
            print('send peak base', TO)
            py_mail('Contrôle des prix', email_content, [], TO, FROM)

        return Response({'result': 'succes'}, status=status.HTTP_201_CREATED)


class PFCPeakDataView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def generate_cockpit_mail(self, pfc, years, pfc_id, hour):
        cet = pytz.timezone('UTC')

        base_data = list(PfcPeakRecord.objects.filter(pfc=pfc, peak='base').values('year', 'value', 'peak'))
        peak_data = list(PfcPeakRecord.objects.filter(pfc=pfc, peak='peak').values('year', 'value', 'peak'))


    def get(self, request, format=None):
        pfc_id = self.request.query_params.get('pfc', '')
        try:
            pfc = PFC.objects.get(id=int(pfc_id)).pfc_id
            years = PfcPeakRecord.objects.filter(pfc_id=int(pfc_id), peak='base').values_list('year', flat=True)
            if PFC.objects.get(id=int(pfc_id)).time:
                pfc = pfc + PFC.objects.get(id=int(pfc_id)).time
            base_data = list(PfcPeakRecord.objects.filter(pfc_id=int(pfc_id)).values('year', 'value', 'peak'))
        except:
            return Response({'result': [], 'years': [], 'pfc': ''}, status=status.HTTP_404_NOT_FOUND)
        return Response({'result': base_data, 'years': years, 'pfc': pfc}, status=status.HTTP_200_OK)



class DeletePFCS(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        # from django.db import connection
        # cursor = connection.cursor()
        # cursor.execute("TRUNCATE TABLE pfc_pfcconsumptionrecord")
        # cursor.execute("TRUNCATE TABLE pfc_pfc CASCADE")
        # cursor.execute("TRUNCATE TABLE pfc_pfcconsumptionfile CASCADE")
        return Response({'data':'ok'}, status=status.HTTP_200_OK)
