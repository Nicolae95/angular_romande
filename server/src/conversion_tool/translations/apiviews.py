from django.shortcuts import *
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from datetime import datetime, timedelta
from django.db.models import Q, F
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
import json
import pytz
import os
import StringIO
import xlsxwriter
from .models import *
from .serializers import *
from companies.models import *


class TranslationViewSet(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        snippets = Translation.objects.all()
        serializer = TranslationSerializer(snippets, context={"request": request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        try:
            request.data['years'] = json.dumps(request.data['years'])
        except:
            return Response({'years':'no valid years'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = TranslationEditSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TranslationByCompanyByYearView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, year, company, site, format=None):
        # cet = pytz.timezone('CET')
        cet = pytz.timezone('UTC')
        cc_from = cet.localize(datetime(int(year), 01, 01, 0, 0), is_dst=None)
        cc_to = cet.localize(datetime(int(year), 12, 31, 23, 59), is_dst=None)
        cet_cc_from = make_aware(cc_from.replace(tzinfo=None), cet, is_dst=None)
        cet_cc_to = make_aware(cc_to.replace(tzinfo=None), cet, is_dst=None)
        print cet_cc_from
        print cet_cc_to
        print Meter.objects.get(meter_sum=True, site_id=int(site), company_id=int(company))
        try:
            meter = Meter.objects.get(meter_sum=True, site_id=int(site), company_id=int(company))
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        records = TranslationRecord.objects.filter(meter = meter, interval_start__gte = cet_cc_from, interval_start__lte=cet_cc_to).values_list('interval_start', 'value').order_by('interval_start')
        print records
        if not records:
            return Response(status=status.HTTP_404_NOT_FOUND)
        reg_list = [[make_naive(f, cet), s] for [f, s] in records]
        records_list = sorted(reg_list, key=lambda x: x[0])
        record_list = [[(f - datetime.utcfromtimestamp(0)).total_seconds() * 1000.0, s] for [f, s] in records_list]

        return Response({'data':'Translated CC', 'records': record_list}, status=status.HTTP_200_OK)


class TranslationsByOfferView(APIView):
    # authentication_classes = (JSONWebTokenAuthentication, )
    # permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):    
        cet = pytz.timezone('UTC')
        pk = self.request.query_params.get('offer', None)
        year = self.request.query_params.get('year', None)
        try:
            offer = Offer.objects.get(emp_id=pk)
        except:
            return Response([], status=status.HTTP_404_NOT_FOUND)

        q = Q()
        if year:
            cc_from = cet.localize(datetime(int(year), 01, 01, 0, 0), is_dst=None)
            cc_to = cet.localize(datetime(int(year), 12, 31, 23, 59), is_dst=None)
            cet_cc_from = make_aware(cc_from.replace(tzinfo=None), cet, is_dst=None)
            cet_cc_to = make_aware(cc_to.replace(tzinfo=None), cet, is_dst=None)
            q = Q(meter=offer.cc, interval_start__gte=cet_cc_from, interval_start__lte=cet_cc_to)
        else:
            return Response([], status=status.HTTP_404_NOT_FOUND)
        
        records = TranslationRecord.objects.filter(q).values('value').annotate(date=F('interval_start')).order_by('date')
        if not records:
            return Response([], status=status.HTTP_404_NOT_FOUND)
        return Response(list(records), status=status.HTTP_200_OK)


class DeleteTranslations(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("TRUNCATE TABLE translations_translationrecord")
        cursor.execute("TRUNCATE TABLE core_energyconsumptionrecord")
        return Response({'data':'ok'}, status=status.HTTP_200_OK)



class TranslationCSVExportView(APIView):
    
    def get(self, request, format=None):
        cet = pytz.timezone('utc')
        year = self.request.query_params.get('year', None)
        site = self.request.query_params.get('site', None)
        cc_from = cet.localize(datetime(int(year), 01, 01, 0, 0), is_dst=None)
        cc_to = cet.localize(datetime(int(year), 12, 31, 23, 59), is_dst=None)
        cet_cc_from = make_aware(cc_from.replace(tzinfo=None), cet, is_dst=None)
        cet_cc_to = make_aware(cc_to.replace(tzinfo=None), cet, is_dst=None)
        print cet_cc_from
        print cet_cc_to
        print Meter.objects.get(meter_sum=True, site_id=int(site))

        # try:
        #     meter = Meter.objects.get(meter_sum=True, site_id=int(site))
        # except:
        #     return Response(status=status.HTTP_404_NOT_FOUND)
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="export.csv"'
        writer = csv.writer(response)
        records = TranslationRecord.objects.filter(meter=meter, interval_start__gte=cet_cc_from, 
                                    interval_start__lte=cet_cc_to).values_list('interval_start', 'value').order_by('interval_start')
        for row in records:
            writer.writerow(row)
        
        return response

    # def get(request):
    #     # Create the HttpResponse object with the appropriate CSV header.
    #     response = HttpResponse(content_type='text/csv')
    #     response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'

    #     writer = csv.writer(response)
    #     writer.writerow(['First row', 'Foo', 'Bar', 'Baz'])
    #     writer.writerow(['Second row', 'A', 'B', 'C', '"Testing"', "Here's a quote"])

    #     return response
