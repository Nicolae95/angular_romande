from django.shortcuts import *
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.utils import jwt_decode_handler
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from datetime import datetime, timedelta
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core import serializers
from django.utils.timezone import get_current_timezone, make_aware, make_naive
from django.utils import timezone
from pytz import country_timezones
import json
import pytz
import os
from client.utils.permision import AdminPermission
from django.views.generic import View
from rest_framework import viewsets
from collections import defaultdict
from operator import itemgetter
from rest_framework import status
from math import sqrt
from .models import *
from core.models import *
from offers.models import *
from offers.serializers import *
from .forms import *
from .serializers import *
from django.db.models import F
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
        print 'weekend ========= ', weekend
        exp = datetime.utcnow() + timedelta(days=int(validation_time) + weekend)
        print 'exp ======= ', exp, 8-exp.isoweekday()
        if exp.isoweekday() > 5:
            return exp.replace(hour=23, minute=59) + timedelta(days=8-exp.isoweekday())
        else:
            return exp.replace(hour=23, minute=59)


class BudgetDataByOfferView(APIView):

    def get(self, request, offer, format=None):
        year = self.request.query_params.get('year', None)
        try:
            offer_data = Offer.objects.get(id=offer)
            if offer_data.pfc_market:
                pfc = Offer.objects.get(id=offer).pfc_market
            else:
                pfc = Offer.objects.get(id=offer).pfc
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        if offer_data.risc: 
            try:
                risc = str(offer_data.risc)[14:-4]
                risc_date =  risc[6:8] + '.' +  risc[4:6] + '.' +  risc[:4] + ' ' + risc[8:10] + ':'  + risc[10:12]
            except:
                risc_date = ''
        else:
            risc_date = ''

        if offer_data.eco:
            try:
                eco = str(offer_data.eco)[8:-4]
                eco_date =  risc[6:8] + '.' +  risc[4:6] + '.' +  risc[:4] + ' ' + risc[8:10] + ':'  + risc[10:12]
            except:
                eco_date = ''
        else:
            eco_date = ''
        
        if (offer_data.offer_type == 'Standart' and offer_data.offer_status == 'indicative' and offer_data.expiration_date.date() < datetime.now().date()):
            if str(request.get_host()) == str('10.4.4.72') or str(request.get_host()) == str('s1empdevdb.pegase.lan') or str(request.get_host()) == str('s1empprddb.pegase.lan'):
                print('get pfcs', request.get_host())
                try:
                    pfc_data = new_data()
                    lpfc = update_data(pfc_data)
                except:
                    print('only romande servers')

            pfc = get_last_pfc()

            if offer_data.pfc != pfc:
                odata = {
                    'id': offer_data,
                    'pfc': pfc.id
                }
                try:
                    offer_data.expiration_date = expiration_date(offer_data.validation_time)
                    serializer = OfferPfcEditSerializer(offer_data, data=odata)
                    print 'valid = ', offer_data, serializer.is_valid()
                    if serializer.is_valid():
                        serializer.save()
                except:
                    print('error on update')

        try:
            if offer_data.pfc_market:
                budgets = Budget.objects.filter(offer_id=offer, pfc_market=pfc).values_list('id', flat=True)
            else:
                budgets = Budget.objects.filter(offer_id=offer, pfc=pfc).values_list('id', flat=True)
                
            if year:
                years = [int(year)]
            else:
                if offer_data.pfc_market:
                    years = Budget.objects.filter(offer_id=offer, pfc_market=pfc).values_list('year', flat=True)
                    years = sorted(reduce(lambda r, v: v in r and r or r + [v], years, []))
                else:
                    years = Budget.objects.filter(offer_id=offer, pfc=pfc).values_list('year', flat=True)
                    years = sorted(reduce(lambda r, v: v in r and r or r + [v], years, []))
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # average_year_price = []
        # average_year_price_final = []
        # for year in years:
        #     average_year_price.append(BudgetAveragePerYear.objects.filter(budget__in=budgets, year=year).values('year', 'value').latest('created'))
        #     average_year_price_final.append(BudgetAveragePerYearRiscs.objects.filter(budget__in=budgets, year=year).values('year', 'value').latest('created'))
        #

        titles = BudgetMedSeasonRecord.objects.filter(budget__in=budgets, year__in=years).annotate(hp_hc=F('schedule__title')).values_list('hp_hc', flat=True)
        title_ids = BudgetMedSeasonRecord.objects.filter(budget__in=budgets, year__in=years).annotate(hp_hc_id=F('schedule__id')).values_list('hp_hc_id', flat=True)
        titles = sorted(reduce(lambda r, v: v in r and r or r + [v], titles, []))
        title_ids = sorted(reduce(lambda r, v: v in r and r or r + [v], title_ids, []))
        print 'titles = ', title_ids

        if Offer.objects.filter(id=offer, offer_status='signee').exists == False:
            return Response(status=status.HTTP_204_NO_CONTENT)

        latest_average_year = BudgetAveragePerYear.objects.filter(budget__in=budgets, year=year).values('year', 'value', 'created').order_by('-created')
        latest_average_year_final = BudgetAveragePerYearRiscs.objects.filter(budget__in=budgets, year=year).values('year', 'value', 'created').order_by('-created')

        average_year_price = BudgetAveragePerYear.objects.filter(budget__in=budgets, year__in=years).values('year', 'value')
        average_year_price_final = BudgetAveragePerYearRiscs.objects.filter(budget__in=budgets, year__in=years).values('year', 'value')

        budget_season = BudgetMedSeasonRecord.objects.filter(budget__in=budgets, year__in=years).annotate(hp_hc=F('schedule__title')).values('year', 'value', 'season', 'hp_hc')
        budget_season_final = BudgetMedSeasonWithRiscsRecord.objects.filter(budget__in=budgets, year__in=years).annotate(hp_hc=F('schedule__title')).values('year', 'value', 'season', 'hp_hc')

        ps1 = ParameterRecord.objects.filter(offer_id=int(offer), parameter=Parameter.objects.get(code='ps1')).values_list('value', flat=True)
        ps2 = ParameterRecord.objects.filter(offer_id=int(offer), parameter=Parameter.objects.get(code='ps2')).values_list('value', flat=True)
        
        exists_ps1 = sum(list(ps1)) != 0
        exists_ps2 = sum(list(ps2)) != 0

        parameters_records = ParameterRecord.objects.filter(offer_id=int(offer)).values('parameter__name', 'year', 'value')
        parameters = ParameterRecord.objects.filter(offer_id=int(offer)).values_list('parameter__name', flat=True)
        parameters = sorted(reduce(lambda r, v: v in r and r or r + [v], parameters, []))
        # pfc = Offer.objects.get(id=offer).pfc
        print pfc

        if offer_data.risc and RiscRecord.objects.filter(file=offer_data.risc, risc__code=None).exclude(rid='').exclude(rid=None).exists():
            if offer_data.pfc_market:
                riscs_records = RiscRecord.objects.filter(file=offer_data.risc, rid=str(offer_data.pfc_market.pfc_id), risc__name__in=['Risque volume', 'Risque PwB']).values('risc__name', 'risc__code', 'year', 'value')
            else:
                riscs_records = RiscRecord.objects.filter(file=offer_data.risc, rid=str(offer_data.pfc.pfc_id), risc__name__in=['Risque volume', 'Risque PwB']).values('risc__name', 'risc__code', 'year', 'value')
                
        else:
            if offer_data.pfc_market:
                riscs_records = RiscRecord.objects.filter(pfc_market=pfc, risc__name__in=['Risque volume', 'Risque PwB']).values('risc__name', 'risc__code', 'year', 'value')
            else:
                riscs_records = RiscRecord.objects.filter(pfc=pfc,  risc__name__in=['Risque volume', 'Risque PwB']).values('risc__name', 'risc__code', 'year', 'value')

        # print riscs_records
        custom = None
        if offer_data.energy_type == None:
            riscs_eco = []
            riscs_e = []
        else:
            if offer_data.eco and RiscRecord.objects.filter(file=offer_data.eco, risc__code=offer_data.energy_type).exclude(rid='').exclude(rid=None).exists():
                if offer_data.pfc_market:
                    custom = offer_data.pfc_market.custom
                    riscs_eco = RiscRecord.objects.filter(file=offer_data.eco, rid=str(offer_data.pfc_market.pfc_id), risc__code=offer_data.energy_type).values('risc__name', 'risc__code', 'year', 'value')
                    riscs_e = RiscRecord.objects.filter(file=offer_data.eco, rid=str(offer_data.pfc_market.pfc_id), risc__code=offer_data.energy_type).values('year', 'value')
                else:
                    custom = None
                    riscs_eco = RiscRecord.objects.filter(file=offer_data.eco, rid=str(offer_data.pfc.pfc_id), risc__code=offer_data.energy_type).values('risc__name', 'risc__code', 'year', 'value')
                    riscs_e = RiscRecord.objects.filter(file=offer_data.eco, rid=str(offer_data.pfc.pfc_id), risc__code=offer_data.energy_type).values('year', 'value')
            else:
                if offer_data.pfc_market:
                    custom = offer_data.pfc_market.custom
                    riscs_eco = RiscRecord.objects.filter(pfc_market=pfc, risc__code=offer_data.energy_type).values('risc__name', 'risc__code', 'year', 'value')
                    riscs_e = RiscRecord.objects.filter(pfc_market=pfc, risc__code=offer_data.energy_type).values('year', 'value')
                else:
                    custom = None
                    riscs_eco = RiscRecord.objects.filter(pfc=pfc, risc__code=offer_data.energy_type).values('risc__name', 'risc__code', 'year', 'value')
                    riscs_e = RiscRecord.objects.filter(pfc=pfc, risc__code=offer_data.energy_type).values('year', 'value')

        # print 'riscs_eco = ', riscs_eco
        if offer_data.risc and RiscRecord.objects.filter(file=offer_data.risc, risc__name='Risque prix').exclude(rid='').exclude(rid=None).exists():
            if offer_data.pfc_market:
                riscs_prix = RiscRecord.objects.filter(file=offer_data.risc, rid=str(offer_data.pfc_market.pfc_id), risc__name='Risque prix').values('risc__name', 'risc__code', 'year', 'value')
            else:
                riscs_prix = RiscRecord.objects.filter(file=offer_data.risc, rid=str(offer_data.pfc.pfc_id), risc__name='Risque prix').values('risc__name', 'risc__code', 'year', 'value')
                
        else:
            if offer_data.pfc_market:
                riscs_prix = RiscRecord.objects.filter(pfc_market=pfc, risc__name='Risque prix').values('risc__name', 'risc__code', 'year', 'value')
            else:            
                riscs_prix = RiscRecord.objects.filter(pfc=pfc, risc__name='Risque prix').values('risc__name', 'risc__code', 'year', 'value')

        # print riscs_prix
        # prixs = riscs_prix
        try:
            if offer_data.validation_time:
                prixs = map(lambda obj: {'risc__name': obj['risc__name'], 'risc__code': obj['risc__code'],
                                        'value': obj['value'] * sqrt(offer_data.validation_time), 'year': obj['year']}, riscs_prix)
            else:
                prixs = riscs_prix
        except:
            prixs = riscs_prix
        
        surgos = ParameterRecord.objects.filter(offer_id=int(offer), parameter=Parameter.objects.get(code='sur_go')).values('year', 'value')
        surgsum = list(riscs_e) + list(surgos)

        riscs_weco = list(riscs_records) + list(prixs)
        riscs_records = list(riscs_records) + list(riscs_eco) + list(prixs)

        print 'riscs_records ========= ', riscs_records

        totals = []
        totals_eco = []

        for year in years:
            totals_eco.append({"year": year, "value": sum(eitem['value'] for eitem in list(filter(lambda eco: eco['year'] == year, surgsum)))})

        for year in years:
            totals.append({"year": year, "value": sum(item['value'] for item in list(filter(lambda risc: risc['year'] == year, riscs_weco)))})

        if offer_data.pfc_market:
            riscs = RiscRecord.objects.filter(pfc_market=pfc, risc__code=None).values_list('risc__name', flat=True)
            risce = RiscRecord.objects.filter(pfc_market=pfc, risc__code=offer_data.energy_type).values_list('risc__name', flat=True)
        else:
            riscs = RiscRecord.objects.filter(pfc=pfc, risc__code=None).values_list('risc__name', flat=True)
            risce = RiscRecord.objects.filter(pfc=pfc, risc__code=offer_data.energy_type).values_list('risc__name', flat=True)
        riscs = sorted(reduce(lambda r, v: v in r and r or r + [v], list(riscs)+list(risce), []))
        # print 'riscs', riscs
        if offer_data.lissage_years:
            import ast
            try:
                lis_data = ast.literal_eval(offer_data.lissage_years)
                lissages = lis_data['lissage_years']['lissage']
            except:
                lissages = []
        
        if offer_data.offer_type == 'Standart':
            if pfc.time:
                pfc_pfc_id = pfc.pfc_id + pfc.time
            else:
                pfc_pfc_id = pfc.pfc_id
        else:
            pfc_pfc_id = pfc.pfc_id
        # if year:
        #     return Response(OrderedDict([('titles', titles),
        #                                  ('title_ids', title_ids),
        #                                  ('years', years),
        #                                  ('price_year', average_year_price),
        #                                  ('price_final_year', average_year_price_final),
        #                                  ('season', budget_season),
        #                                  ('season_final', budget_season_final),
        #                                  ('riscs_records', riscs_records),
        #                                  ('riscs', riscs),
        #                                  ('parameters_records', parameters_records),
        #                                  ('parameters', parameters),
        #                                  ('lissages', lissages),
        #                                  ('pfc', pfc.pfc_id),
        #                                  ('comment', offer_data.comment),
        #                                  ('totals', totals)
        #                  ]), status=status.HTTP_200_OK)
        # else:
        return Response(OrderedDict([('offer_type', offer_data.shedules.all().values_list('id', flat=True)),
                                        ('titles', titles),
                                        ('title_ids', title_ids),
                                        ('years', years),
                                        ('price_year', average_year_price),
                                        ('price_final_year', average_year_price_final),
                                        ('season', budget_season),
                                        ('season_final', budget_season_final),
                                        ('riscs_records', riscs_records),
                                        ('riscs', riscs),
                                        ('parameters_records', parameters_records),
                                        ('parameters', parameters),
                                        ('lissages', lissages),
                                        ('pfc', pfc_pfc_id),
                                        ('comment', offer_data.comment),
                                        ('risc_date', risc_date),
                                        ('eco_date', eco_date),
                                        ('totals', totals),
                                        ('totals_eco', totals_eco),
                                        ('custom_eco', custom),
                                        ('exists_ps1', exists_ps1),
                                        ('exists_ps2', exists_ps2)
                                        ]), status=status.HTTP_200_OK)


class WeeklyByCompanyByYearView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, year, company, site, format=None):
        # cet = pytz.timezone('CET')
        if year == '' or company == '':
            return Response({'Error': 'Missing data'}, status=status.HTTP_404_NOT_FOUND)
        cet = pytz.timezone('UTC')
        cc_from = cet.localize(datetime(int(year), 01, 01, 0, 0), is_dst=None)
        cc_to = cet.localize(datetime(int(year), 12, 31, 23, 59), is_dst=None)
        cet_cc_from = make_aware(cc_from.replace(tzinfo=None), cet, is_dst=None)
        cet_cc_to = make_aware(cc_to.replace(tzinfo=None), cet, is_dst=None)
        print 'weekly', cet_cc_from
        print 'weekly', cet_cc_to
        try:
            print site
            meter = Meter.objects.get(meter_sum=True, site_id=int(site))
            print meter
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # budget = Budget.objects.get(cc=meter, year=int(year))
        # print meter
        # print budget
        # records = BudgetWeeklyRecord.objects.filter(budget = budget, year = int(year)).values_list('hour', 'value').order_by('hour')
        # if not records:
        #     return Response(status=status.HTTP_404_NOT_FOUND)
        # reg_list = [[make_naive(f, cet), s] for [f, s] in records]
        # records_list = sorted(reg_list, key=lambda x: x[0])
        # record_list = [[(f - datetime.utcfromtimestamp(0)).total_seconds() * 1000.0, s] for [f, s] in records_list]
        # return Response({'data':'Weekly', 'records':record_list}, status=status.HTTP_200_OK)


class BudgetListViewSet(APIView):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated, AdminPermission, )

    def get(self, request, format=None):
        # print 'data = ', request.META['HTTP_AUTHORIZATION'][4:]
        # print type(jwt_decode_handler(request.META['HTTP_AUTHORIZATION'][4:]))
        # decoded = jwt_decode_handler(request.META['HTTP_AUTHORIZATION'][4:])
        # print decoded['role']
        snippets = Budget.objects.all()
        serializer = BudgetSerializer(snippets, context={"request": request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = BudgetCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BudgetByIdView(APIView):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated, AdminPermission, )

    def get(self, request, pk, format=None):
        snippet = get_object_or_404(Budget, id=pk)
        serializer = BudgetSerializer(snippet)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        snippet = get_object_or_404(Budget, id=pk)
        serializer = BudgetCreateSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        snippet = get_object_or_404(Budget, id=pk)
        snippet.delete()
        return Response(status=status.HTTP_200_OK)


class BudgetByOfferView(APIView):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated, AdminPermission, )

    def get(self, request, site, format=None):
        # snippet = get_object_or_404(Budget, offer_id=int(site))
        # serializer = BudgetSerializer(snippet)
        return Response(status=status.HTTP_200_OK)


class BudgetRecordViewSet(APIView):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated, AdminPermission, )

    def get(self, request, format=None):
        snippets = BudgetRecord.objects.all()
        serializer = BudgetRecordSerializer(snippets, context={"request": request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BudgetHistoryDataByOfferView(APIView):

    def get(self, request, offer, format=None):
        try:
            offer_data = Offer.objects.get(id=offer)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            budgets = Budget.objects.filter(offer_id=offer).values_list('id', flat=True)
            years = Budget.objects.filter(offer_id=offer).values_list('year', flat=True)
            years = sorted(reduce(lambda r, v: v in r and r or r + [v], years, []))
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        history = defaultdict(list)
        for year in years:
            datas = list(BudgetAveragePerYearRiscs.objects.filter(budget__in=budgets, year=year).values_list('budget__pfc__pfc_id', 'value'))
            datas_new = map(lambda x: [datetime.strptime(x[0], '%d.%m.%Y'), x[1]], datas)
            datas_sort = sorted(datas_new, key=lambda x: x[0])
            datas_pre = map(lambda x: [x[0].strftime("%d.%m.%Y"), x[1]], datas_sort)
            history[year] = datas_pre

        return Response(OrderedDict([('years', years),
                                     ('history', history),
                                    ]), status=status.HTTP_200_OK)


class OfferBudgetLisForceViewSet(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)


    def post(self, request, format=None):
        print request.data
        try:
            meter = Meter.objects.get(site_id=int(request.data['offer']['site']), meter_sum=True)
            peak = Shedule.objects.get(title='Peak')
            offpeak = Shedule.objects.get(title='OffPeak')
            years = ','.join(str(e) for e in request.data['offer']['anii'])
            years_str = [str(e) for e in request.data['offer']['anii']]
            print meter, peak, offpeak, years
        except:
             return Response(status=status.HTTP_400_BAD_REQUEST)

        budgets = defaultdict()
        offer, createro = Offer.objects.get_or_create(name='Lis_' + request.data['offer']['name'], offer_status='signee',
                                    company_id=request.data['offer']['company']['id'],  cc=meter, years=years, lis_force=True)
        offer.lis_manual_expire = datetime.now() + timedelta(minutes=20)
        offer.save()

        for year in request.data['offer']['anii']:
            bg, createrb = Budget.objects.get_or_create(offer=offer, year=int(year), cc=meter, budget_id='Lis_' + request.data['offer']['name'])
            budgets[str(year)] = bg

        print('budgets == ', budgets)
        for prix in request.data['offer']['prix']:
            if 'ete_hp' in prix.keys(): # peak
                for year, ete_hp in prix['ete_hp'].iteritems():
                    if str(year) in years_str:
                        print year, ete_hp
                        bg_ete_hp, cr1 = BudgetMedSeasonRecord.objects.get_or_create(budget=budgets[str(year)], year=int(year), schedule=peak, season='Summer')
                        bg_ete_hp.value = float(ete_hp)
                        bg_ete_hp.save()
                # print prix
            if 'ete_hc' in prix.keys(): # offpeak
                for year, ete_hc in prix['ete_hc'].iteritems():
                    if str(year) in years_str:
                        print year, ete_hc
                        bg_ete_hc, cr2 = BudgetMedSeasonRecord.objects.get_or_create(budget=budgets[str(year)], year=int(year), schedule=offpeak, season='Summer')
                        bg_ete_hc.value = float(ete_hc)
                        bg_ete_hc.save()
                # print prix
            if 'hiver_hp' in prix.keys():
                for year, hiver_hp in prix['hiver_hp'].iteritems():
                    if str(year) in years_str:
                        print year, hiver_hp
                        bg_hiver_hp, cr3 = BudgetMedSeasonRecord.objects.get_or_create(budget=budgets[str(year)],  year=int(year), schedule=peak, season='Winter')
                        bg_hiver_hp.value = float(hiver_hp)
                        bg_hiver_hp.save()
                # print prix
            if 'hiver_hc' in prix.keys():
                for year, hiver_hc in prix['hiver_hc'].iteritems():
                    if str(year) in years_str:
                        print year, hiver_hc
                        bg_hiver_hc, cr4 = BudgetMedSeasonRecord.objects.get_or_create(budget=budgets[str(year)],  year=int(year), schedule=offpeak,  season='Winter')
                        bg_hiver_hc.value = float(hiver_hc)
                        bg_hiver_hc.save()
                # print 'hiver_hc == ', prix

        for prix_f in request.data['offer']['prix_f']:
            if 'ete_hp' in prix_f.keys():  # peak
                for year, ete_hp in prix_f['ete_hp'].iteritems():
                    if str(year) in years_str:
                        print year, ete_hp
                        bg_ete_hp_f, cr5 = BudgetMedSeasonWithRiscsRecord.objects.get_or_create(budget=budgets[str(year)], year=int(year), schedule=peak, season='Summer')
                        bg_ete_hp_f.value = float(ete_hp)
                        bg_ete_hp_f.save()
                # print prix_f
            if 'ete_hc' in prix_f.keys():  # offpeak
                for year, ete_hc in prix_f['ete_hc'].iteritems():
                    if str(year) in years_str:
                        print year, ete_hc
                        bg_ete_hc_f, cr6 = BudgetMedSeasonWithRiscsRecord.objects.get_or_create(budget=budgets[str(year)], year=int(year), schedule=offpeak, season='Summer')
                        bg_ete_hc_f.value = float(ete_hc)
                        bg_ete_hc_f.save()
                # print prix
            if 'hiver_hp' in prix_f.keys():
                for year, hiver_hp in prix_f['hiver_hp'].iteritems():
                    if str(year) in years_str:
                        print year, hiver_hp
                        bg_hiver_hp_f, cr7 = BudgetMedSeasonWithRiscsRecord.objects.get_or_create(budget=budgets[str(year)],  year=int(year), schedule=peak, season='Winter')
                        bg_hiver_hp_f.value = float(hiver_hp)
                        bg_hiver_hp_f.save()
                # print prix
            if 'hiver_hc' in prix_f.keys():
                for year, hiver_hc in prix_f['hiver_hc'].iteritems():
                    if str(year) in years_str:
                        print year, hiver_hc
                        bg_hiver_hc_f, cr8 = BudgetMedSeasonWithRiscsRecord.objects.get_or_create(budget=budgets[str(year)],  year=int(year), schedule=offpeak, season='Winter')
                        bg_hiver_hc_f.value = float(hiver_hc)
                        bg_hiver_hc_f.save()
                # print 'hiver_hc == ', prix

        for year, omoney_i in request.data['offer']['omoney_i'].iteritems():
            if str(year) in years_str:
                brwe, cr9 = BudgetAverageWithoutEfort.objects.get_or_create(budget=budgets[str(year)], year=int(year))
                brwe.value = float(omoney_i)
                brwe.save()
                brper, cr10 = BudgetAveragePerYear.objects.get_or_create(budget=budgets[str(year)], year=int(year))
                brper.value = float(omoney_i)
                brper.save()
                brperc, crc10 = BudgetAverageClean.objects.get_or_create(budget=budgets[str(year)], year=int(year))
                brperc.value = float(omoney_i)
                brperc.save()

        for year, o_fin_money_i in request.data['offer']['o_fin_money_i'].iteritems():
            if str(year) in years_str:
                print year, o_fin_money_i
                bgofin, cr11 = BudgetAveragePerYearRiscs.objects.get_or_create(budget=budgets[str(year)], year=int(year))
                bgofin.value = float(o_fin_money_i)
                bgofin.save()

        # print 'offer lis force prix_f = ', request.data['offer']['prix_f']
        return Response({'offer': offer.id}, status=status.HTTP_200_OK)
