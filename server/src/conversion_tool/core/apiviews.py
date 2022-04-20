from django.shortcuts import *
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from datetime import datetime, timedelta
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core import serializers
from django.utils.timezone import get_current_timezone, make_aware, make_naive
from django.utils import timezone
from pytz import country_timezones
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpRequest
from xlrd import open_workbook, xldate
from django.views.generic import View
from rest_framework import viewsets
from collections import defaultdict
from operator import itemgetter
from rest_framework import status
from django.shortcuts import *
from .models import *
from .serializers import *
from companies.models import *
from translations.models import *
from typepondere.models import *
from django.db.models import Sum
from logic.db.upload import upload_db, upload_null
import json
import pytz
import os
import io
import StringIO
import xlsxwriter


class SheduleListViewSet(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        snippets = Shedule.objects.all()
        serializer = SheduleSerializer(snippets, context={"request": request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = SheduleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CCByCompanyByYearView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, year, company, site, format=None):
        # cet = pytz.timezone('CET')
        print company
        if year == '' or company == '':
            return Response({'Error': 'Missing data'}, status=status.HTTP_404_NOT_FOUND)
        cet = pytz.timezone('UTC')
        cc_from = cet.localize(datetime(int(year), 01, 01, 0, 0), is_dst=None)
        cc_to = cet.localize(datetime(int(year), 12, 31, 23, 59), is_dst=None)
        cet_cc_from = make_aware(cc_from.replace(tzinfo=None), cet, is_dst=None)
        cet_cc_to = make_aware(cc_to.replace(tzinfo=None), cet, is_dst=None)
        print cet_cc_from
        print cet_cc_to
        try:
            meter = Meter.objects.get(meter_sum=True, site_id=int(site), company_id=int(company))
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        records = EnergyConsumptionRecord.objects.filter(meter = meter, interval_start__gte = cet_cc_from, interval_start__lte=cet_cc_to).values_list('interval_start', 'value').order_by('interval_start')
        if not records:
            return Response(status=status.HTTP_404_NOT_FOUND)
        reg_list = [[make_naive(f, cet), s] for [f, s] in records]
        records_list = sorted(reg_list, key=lambda x: x[0])
        record_list = [[(f - datetime.utcfromtimestamp(0)).total_seconds() * 1000.0, s] for [f, s] in records_list]

        # record_list = ['[Date.UTC('+str(f.year)+','+str(f.month)+','+str(f.day)+','+str(f.hour)+','+str(f.minute)+'),'+ str(s)+'],' for [f, s] in records_list]
        # record_string = '([\n'+'\n'.join(record_list)+']);'
        # d = len(record_string)
        # records_string = ''.join([record_string[i] for i in range(len(record_string)) if i  != d-4])
        return Response({'data':'CC', 'records':record_list}, status=status.HTTP_200_OK)


class CCWeeklyByCompanyByYearView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, year, site, company, format=None):
        # cet = pytz.timezone('CET')
        if year == '' or company == '':
            return Response({'Error': 'Missing data'}, status=status.HTTP_404_NOT_FOUND)
        try:
            meter = Meter.objects.get(meter_sum=True, site_id=int(site), company_id=int(company))
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        weekly = WeeklyRecord.objects.filter(meter=meter, year=int(year)).values_list('hour', 'value')
        if not weekly:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response({'data':'Weekly', 'records':weekly}, status=status.HTTP_200_OK)


class FilesUploadView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    parser_classes = (FormParser, MultiPartParser)
    def post(self, request, format=None):
        print request.data['years'].split(',')
        if (request.data['site'] == '' or request.data['meters'] == '' or request.data['year'] == '' or (request.data['onlyname'] == 'false'
            and request.data['mensue'] == 'false' and request.data['hphc'] == 'false' and request.FILES.getlist('files') == [])
            or request.data['company'] == '' or request.data['years'] == '' or request.data['dates'] == ''):
            return Response({'Error': 'Missing data'}, status=status.HTTP_404_NOT_FOUND)
        data = request.data['dates'].split(',')
        obj = {}
        for index, y in enumerate(request.data['years'].split(',')):
            obj[y] = data[index]

        if request.data['onlyname'] == 'true' or request.data['mensue'] == 'true' or request.data['hphc'] == 'true':
            multisite = False
            if request.data['multisite'].lower() == "true":
                multisite = True
            site = Site(name = request.data['site'], year = int(request.data['year']), company_id = int(request.data['company']), multisite = multisite)
            site.save()
            meters = []
            for meter in request.data['meters'].split(','):
                print 'meters', meter
                meter = Meter.objects.filter(id=int(meter))
                if not meter:
                    return Response({'meters':'No such meters'}, status=status.HTTP_400_BAD_REQUEST)
                elif meter[0].meter_sum:
                    pass
                else:
                    meter.update(site_id=site.id)
                    meters.append(meter[0])
            # site.meters.add(*meters)
            print site.id, 'Virtual Sum' + str(site.id)
            msum = Meter.objects.create(meter_id='Virtual_Sum_' + str(site.id), meter_sum = True, site=site, company=site.company)
            # data_year = int(datetime.now().year)-1
            try:
                tp = ProfileTypePondere.objects.get(year = int(request.data['year']))
            except:
                return Response({'meters':'No such pondere for this year'}, status=status.HTTP_400_BAD_REQUEST)
            records = ProfileTypePondereConsumptionRecord.objects.filter(profile = tp)
            from itertools import groupby
            invoices = ProfileTypePondereConsumptionRecord.objects.filter(profile = tp).only('interval_start', 'value').order_by('interval_start')
            profile_sum = ProfileTypePondereConsumptionRecord.objects.filter(profile = tp).aggregate(Sum('value'))
            print 'only invoices == ', invoices
            month_totals = {
                k: sum(x.value for x in g)
                for k, g in groupby(invoices, key=lambda i: i.interval_start.month)
            }
            stream = StringIO.StringIO()
            writer = csv.writer(stream, delimiter='\t')
            if request.data['onlyname'] == 'true':
                for record in records:
                    print 'anual volume', record.value
                    val = (float(str(request.data['volume']).replace("'", "")) / float(profile_sum['value__sum'])) * record.value
                    writer.writerow([datetime.now(), datetime.now(), int(msum.id), val, record.interval_start, timedelta(hours=1), 'kWh'])

            if request.data['mensue'] == 'true' or request.data['hphc'] == 'true':
                months = request.data['months'].split(',')
                for record in records:
                    print 'months', str(months[record.interval_start.month-1]).replace("'", ""), float(month_totals[record.interval_start.month]), record.value
                    val = (float(str(months[record.interval_start.month-1]).replace("'", "")) / float(month_totals[record.interval_start.month])) * record.value
                    writer.writerow([datetime.now(), datetime.now(), int(msum.id), val, record.interval_start, timedelta(hours=1), 'kWh'])
            upload_null(stream)
            trans = Translation(cc = msum, years = json.dumps(obj))
            trans.save()
            trans.upload_meter()

        if request.FILES.getlist('files') != []:
            print 'sum_exists = ', request.data['sum_exists']
            multisite = False
            sum_exists = False

            if request.data['sum_exists'].lower() == "true":
                sum_exists = True
            if request.data['multisite'].lower() == "true":
                multisite = True
            print 'multisite = ', multisite
            site = Site(name = request.data['site'], year = int(request.data['year']), company_id = int(request.data['company']), multisite = multisite)
            site.save()
            meters = []
            msum = Meter.objects.create(meter_id='Virtual_Sum_' + str(site.id), meter_sum = True, site=site, company=site.company)
            meters.append(msum)
            # if multisite == True or (multisite == False and sum_exists == True):
            #     meters.append(msum[0])
            #     print meters, msum[0]

            # if multisite == True or (multisite == False and sum_exists == False):
            for meter in request.data['meters'].split(','):
                print 'meters', meter
                meter = Meter.objects.filter(id=int(meter))
                if not meter:
                    return Response({'meters':'No such meters'}, status=status.HTTP_400_BAD_REQUEST)
                elif meter[0].meter_sum:
                    pass
                else:
                    meter.update(site_id=site.id)
                    meters.append(meter[0])
            print 'meters', meters
            CONTENT_TYPES = ['.xlsx', '.xls']
            
            for fil in request.FILES.getlist('files'):
                filename, file_extension = os.path.splitext(fil.name)
                if file_extension not in CONTENT_TYPES:
                    return Response({'Error': 'File bad format'}, status=status.HTTP_400_BAD_REQUEST)

            for index, f in enumerate(request.FILES.getlist('files')):
                instance = EnergyConsumptionFile(data_file = f, site_id = site.id, multi = multisite)
                instance.save()
                if multisite == False:
                    instance.meters.add(meters[index])
                else:
                    instance.meters.add(*meters)
                instance.process_file()
            if  multisite == True:
                instance.sum_meters(msum)
            try:
                trans = Translation(cc = msum, years = json.dumps(obj))
                trans.save()
                trans.upload_meter()
            except:
                return Response({'received data': 'Error or data is missing'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'received data': len(request.data)})


class VolumesViewSet(APIView):
    # authentication_classes = (JSONWebTokenAuthentication, )
    # permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        snippet = get_object_or_404(Offer, id=pk)
        try:
            energy_meds = EnergyConsumptionRecord.objects.filter(meter=snippet.cc).only(
                'interval_start', 'value').order_by('interval_start')
            
            trans_meds = TranslationRecord.objects.filter(meter=snippet.cc).only(
                'interval_start', 'value').order_by('interval_start')
            
            year_sum = {
                k: sum(x.value for x in g)
                for k, g in groupby(list(energy_meds)+list(trans_meds), key=lambda i: i.interval_start.year)
            }
            years_list = []
            for year, value in year_sum.iteritems():
                years_list.append({'year': year, 'value': "{:,}".format(
                    int(round(value))).replace(",", "'")})
                # years_list.append({'year': year, 'value': value})
        except:
            years_list = []
        return Response(years_list, status=status.HTTP_200_OK)
