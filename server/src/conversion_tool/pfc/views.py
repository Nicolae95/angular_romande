from django.shortcuts import *
from rest_framework.parsers import MultiPartParser, FormParser
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
import json
import pytz
import os

from django.views.generic import View
from rest_framework import viewsets
from collections import defaultdict
from operator import itemgetter

from .models import *
from .forms import *

@login_required(login_url="/login/")
def pfc_upload_files(request):
    if request.method == 'POST':
        form = PfcConsumptionFileForm(request.POST, request.FILES)
        if form.is_valid():
            pfc, created  = PFC.objects.get_or_create(pfc_id=timezone.now().strftime("%d.%m.%Y %H:%M")[:10])
            files = []
            for f in request.FILES.getlist('data_file'):
                instance = PfcConsumptionFile(data_file = f, pfc=pfc)
                instance.save()
            return HttpResponseRedirect('/')
    else:
        form = PfcConsumptionFileForm()
    return render(request, 'tool/pfc/upload.html', {'form': form})


@login_required(login_url="/login/")
def pfc_market_upload_files(request):
    if request.method == 'POST':
        form = PfcConsumptionFileForm(request.POST, request.FILES)
        if form.is_valid():
            pfc, created  = PFCMarket.objects.get_or_create(pfc_id=timezone.now().strftime("%d.%m.%Y %H:%M")[:10])
            files = []
            for f in request.FILES.getlist('data_file'):
                instance = PfcConsumptionFile(data_file = f, pfc_market=pfc)
                instance.save()
            return HttpResponseRedirect('/')
    else:
        form = PfcConsumptionFileForm()
    return render(request, 'tool/pfc/market_upload.html', {'form': form})
