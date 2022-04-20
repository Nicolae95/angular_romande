# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import *
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.renderers import JSONRenderer
from datetime import datetime, timedelta
from django.db.models import Q
from django.core import serializers
from django.utils.timezone import get_current_timezone, make_aware, make_naive
from django.utils import timezone
from pytz import country_timezones
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpRequest
from rest_framework.pagination import LimitOffsetPagination
import json
import pytz
import os
import uuid
import requests
from collections import defaultdict
from operator import itemgetter
from rest_framework import status
from user import User

api = 'http://energymarketprice.com/WebServices'


class DatahubUnitsViewSet(APIView):
    # authentication_classes = (JSONWebTokenAuthentication, )
    # permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        unitenergy = self.request.query_params.get('unitenergy', '')
        resource = self.request.query_params.get('resource', '')
        stype = self.request.query_params.get('type', '')
        subtype = self.request.query_params.get('subtype', '')
        print self.request.query_params.get('resource', '')
        url = api + '/DataHub'
        if unitenergy:
            url = url + '?unitenergy=' + unitenergy
        if unitenergy and resource:
            url = url + '&resource=' + resource
        if unitenergy and resource and stype:
            url = url + '&type=' + stype
        if unitenergy and resource and stype and subtype:
            url = url + '&subtype=' + subtype

        user = User()
        need_login = False

        user.get_token_file()
        if not user.token:
            need_login = True
        
        headers = {
            'content-type': 'application/json',
            'AUTH': user.token,
        }
        try:
            response = requests.get(url, headers=headers)
            return Response(json.loads(response.content), status=status.HTTP_200_OK)
        except:
            need_login = True

        if need_login == True:
            user.login()
            if user.token == '':
                return Response(status=status.HTTP_400_BAD_REQUEST)
            headers = {
                'content-type': 'application/json',
                'AUTH': user.token,
            }
            try:
                response = requests.get(url, headers=headers)
                # print url, json.loads(response.content)
                return Response(json.loads(response.content), status=status.HTTP_200_OK)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)


class DatahubMarketViewSet(APIView):
    # authentication_classes = (JSONWebTokenAuthentication, )
    # permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        user = User()
        need_login = False

        #  Token from file
        user.get_token_file()
        if user.token == '':
            need_login = True
        headers = {
            'content-type': 'application/json',
            'AUTH': user.token,
        }
        try:
            response = requests.patch(api + '/DataHub', json.dumps(request.data), headers=headers)
            return Response(json.loads(response.content), status=status.HTTP_200_OK)
        except:
            need_login = True

        #  Login
        if need_login == True:
            user.login()
            if user.token == '':
                return Response(status=status.HTTP_400_BAD_REQUEST)
            headers = {
                'content-type': 'application/json',
                'AUTH': user.token,
            }
            try:
                response = requests.patch(
                    api + '/DataHub', json.dumps(request.data), headers=headers)
                # print 'response == ', json.loads(response.content)
                return Response(json.loads(response.content), status=status.HTTP_200_OK)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)


class ChartMarketViewSet(APIView):
    # authentication_classes = (JSONWebTokenAuthentication, )
    # permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        cid = self.request.query_params.get('cid', '')
        dfrom = self.request.query_params.get('dfrom', '')
        dto = self.request.query_params.get('dto', '')        
        try:
            response = requests.get('http://www.marketpricesolutions.com/apitest.asp?act=getdataforchart&cid=' + cid + '&dfrom=' + dfrom + '&dto=' + dto)
            return Response(json.loads(response.text), status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class TabelMarketViewSet(APIView):
    # authentication_classes = (JSONWebTokenAuthentication, )
    # permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        cid = self.request.query_params.get('cid', '')     
        try:
            response = requests.get('http://www.marketpricesolutions.com/apitest.asp?act=datafortableromande&cid=' + cid )
            return Response(json.loads(response.text), status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
