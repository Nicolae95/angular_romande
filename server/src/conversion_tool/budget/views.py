from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import pytz
from django.utils.timezone import get_current_timezone, make_aware, make_naive
from pytz import country_timezones
import os
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpRequest

from .models import *
from .forms import *
from pfc.models import *
from core.models import *


@login_required(login_url="/login/")
def create_budget(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            years = []
            for entry in EnergyConsumptionRecord.objects.filter(meter = form.cleaned_data.get('cc')).values_list('interval_start', flat=True):
                if entry.date().year not in years:
                    years.append(entry.date().year)
            for year in years:
                print year
                if form.cleaned_data.get('pfc'):
                    print 'pfc'
                    instance = Budget(cc = form.cleaned_data.get('cc'), pfc = form.cleaned_data.get('pfc'), year = year)
                else:
                    print 'pfc_market'
                    instance = Budget(cc = form.cleaned_data.get('cc'), pfc_market = form.cleaned_data.get('pfc_market'), year = year)
                instance.save()
                instance.produce_report()
            return HttpResponseRedirect('/')

    else:
        form = BudgetForm()
    return render(request, 'tool/budget/upload.html', {'form': form})
