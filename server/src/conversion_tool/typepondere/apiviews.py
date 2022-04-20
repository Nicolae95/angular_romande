from django.shortcuts import *
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.utils import jwt_decode_handler
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime, timedelta
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core import serializers
from django.utils.timezone import get_current_timezone, make_aware, make_naive
import json
import pytz
import StringIO
import xlsxwriter
from xlrd import open_workbook, xldate
from rest_framework import viewsets
from collections import defaultdict
from operator import itemgetter
from rest_framework import status
from .models import *
from .serializers import *


class PondereRecordsYearView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, pondere, year, format=None):
        # cet = pytz.timezone('CET')
        if year == '':
            return Response({'Error': 'Missing data'}, status=status.HTTP_404_NOT_FOUND)
        cet = pytz.timezone('UTC')
        cc_from = cet.localize(datetime(int(year), 01, 01, 0, 0), is_dst=None)
        cc_to = cet.localize(datetime(int(year), 12, 31, 23, 59), is_dst=None)
        cet_cc_from = make_aware(cc_from.replace(tzinfo=None), cet, is_dst=None)
        cet_cc_to = make_aware(cc_to.replace(tzinfo=None), cet, is_dst=None)
        print cet_cc_from
        print cet_cc_to
        try:
            profile = ProfileTypePondere.objects.get(id=int(pondere))
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        records = ProfileTypePondereConsumptionRecord.objects.filter(profile=profile, interval_start__gte = cet_cc_from, interval_start__lte=cet_cc_to).values_list('interval_start', 'value').order_by('interval_start')
        if not records:
            return Response(status=status.HTTP_404_NOT_FOUND)
        reg_list = [[make_naive(f, cet), s] for [f, s] in records]
        records_list = sorted(reg_list, key=lambda x: x[0])
        record_list = [[(f - datetime.utcfromtimestamp(0)).total_seconds() * 1000.0, s] for [f, s] in records_list]
        return Response({'data':'Type', 'records':record_list}, status=status.HTTP_200_OK)


class PondereViewSet(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        snippets = ProfileTypePondere.objects.all().order_by('-pk')
        serializer = ProfileTypePondereSerializer(snippets, context={"request": request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PondereByIdView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)
    # def get_object(self, pk):
    #     try:
    #         return ProfileType.objects.get(id=int(pk))
    #     except ProfileType.DoesNotExist:
    #         return Response(status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk, format=None):
        snippet = get_object_or_404(ProfileType, id=pk)
        serializer = ProfileTypePondereSerializer(snippet)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        snippet = get_object_or_404(ProfileType, id=pk)
        serializer = ProfileTypePondereSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        snippet = get_object_or_404(ProfileType, id=pk)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TypePondereFilesUploadView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)
    parser_classes = (FormParser, MultiPartParser)
    def post(self, request, format=None):
        print request.data
        if request.data['name'] == '' or request.data['year'] == '':
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if request.FILES.getlist('files') == []:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        for f in request.FILES.getlist('files'):
            instance = ProfileTypePondere(data_file = f, name = 'CC Type ' + request.data['name'] + ' - ' + str(request.data['year']), year = int(request.data['year']))
            instance.save()
        return Response({'received data': len(request.data)}, status=status.HTTP_201_CREATED)
