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

class OfferPdfUnsignedExportView(View):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        fid = request.GET['file']
        try:
            offer = Offer.objects.get(id=int(fid))
            pdf = offer.unsigned_file
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="{}"'.format(str(pdf))
        except:
            return response
        return response

class OfferPdfSignedExportView(View):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, *args, **kwargs):
        fid = request.GET['file']
        try:
            offer = Offer.objects.get(id=int(fid))
            pdf = offer.signed_file
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="{}"'.format(str(pdf))
        except:
            return response
        return response


