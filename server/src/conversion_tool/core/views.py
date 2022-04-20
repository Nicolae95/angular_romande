from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
from django.shortcuts import redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
import json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core import serializers
import pytz
from django.utils.timezone import get_current_timezone, make_aware, make_naive
from pytz import country_timezones
import os
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpRequest

from geo.models import Location, Holiday
from core.models import *
from core.forms import *
from companies.forms import CompanyForm, MeterForm, SiteForm
from companies.models import Company, Meter, Site
from core.serializers import ReportSerializer

from django.shortcuts import render
from django.views.generic import View
from rest_framework import viewsets

from collections import defaultdict
from operator import itemgetter

timezone_country = {}
for countrycode in country_timezones:
    timezones = country_timezones[countrycode]
    for timezone in timezones:
        timezone_country[timezone] = countrycode
        timezone_country[countrycode] = timezone

# from sheds import *

@login_required(login_url="/login/")
def sheds(request, id):
    try:
        shedules = Shedule.objects.filter(country = id)
        data = serializers.serialize("json", shedules)
        return HttpResponse(data, content_type='application/json')
    except:
        return HttpResponse({'shedules':'No Shedules'}, content_type='application/json')

@login_required(login_url="/login/")
def units(request, meter):
    try:
        units = EnergyConsumptionRecord.objects.filter(meter = meter).order_by('unit').distinct('unit')
        data = serializers.serialize("json", units)
        return HttpResponse(data, content_type='application/json')
    except:
        return HttpResponse({'No Units'}, content_type='application/json')

@login_required(login_url="/login/")
def chart(request, meter, datetime_from, datetime_to, shedule, unit):
    info = {'meter':meter, 'datetime_from':datetime_from, 'datetime_to':datetime_to, 'shedule':shedule, 'unit':unit}
    if shedule != '0':
        try:
            shed = Shedule.objects.get(id = shedule)
            countryz = shed.country.country
            cet = pytz.timezone(timezone_country[str(countryz)])
        except:
            return render(request, 'tool/notfound/404.html', {'page': 'Data chart', 'error':'404 Not found'})
    else:
        cet = pytz.timezone('CET')
        uc = pytz.timezone('UTC')

    try:
        # cet = pytz.timezone('CET')
        date_from = datetime.strptime(datetime_from, "%Y%m%d").date()
        date_to = datetime.strptime(datetime_to, "%Y%m%d").date() + timedelta(days=1)
        m = Meter.objects.get(meter_id = meter)
        flag = False
        if unit == 'None':
            records = EnergyConsumptionRecord.objects.filter(meter = m, interval_start__gte = date_from, interval_start__lte=date_to).values_list('interval_start', 'value').order_by('interval_start')
        else :
            u = unit.replace('_', '/')
            records = EnergyConsumptionRecord.objects.filter(meter = m, interval_start__gte = date_from, interval_start__lte=date_to, unit=u).values_list('interval_start', 'value').order_by('interval_start')
            print records
        if 'pfc' in meter.lower():
            reg_list = [[make_naive(f, pytz.timezone('UTC')), s] for [f, s] in records]
        elif 'cc' in meter.lower():
            flag = True
            reg_list = [[make_naive(f, pytz.timezone('UTC')), s] for [f, s] in records]
        else:
            reg_list = [[make_naive(f, cet), s] for [f, s] in records]
        records_list = sorted(reg_list, key=lambda x: x[0])
        record_list = ['[Date.UTC('+str(f.year)+','+str(f.month-1)+','+str(f.day)+','+str(f.hour)+','+str(f.minute)+'),'+ str(s)+'],' for [f, s] in records_list]
        record_string = '([\n'+'\n'.join(record_list)+']);'
        # print record_string
        d = len(record_string)
        records_string = ''.join([record_string[i] for i in range(len(record_string)) if i  != d-4])
        # print records_string

    except:
        return render(request, 'tool/notfound/404.html', {'page': 'Data chart', 'error': '404 Not found'})
    return render(request, 'tool/chart/report.html', {'records': records_string, 'info': info, 'meter': m, 'flag':flag})


@login_required(login_url="/login/")
def chart_weekly(request, meter, datetime_from, datetime_to,  shedule, unit):
    info = {'meter':meter, 'datetime_from':datetime_from, 'datetime_to':datetime_to, 'shedule':shedule, 'unit':unit}
    cet = pytz.timezone('UTC')

    try:
        # cet = pytz.timezone('CET')
        date_from = datetime.strptime(datetime_from, "%Y%m%d").date()
        date_to = datetime.strptime(datetime_to, "%Y%m%d").date()
        print date_from
        m = Meter.objects.get(meter_id = meter)
        if unit == 'None':
            records = EnergyConsumptionRecord.objects.filter(meter = m, interval_start__gte = date_from, interval_start__lte=date_to).values('interval_start', 'value').order_by('interval_start')
        else :
            u = unit.replace('_', '/')
            records = EnergyConsumptionRecord.objects.filter(meter = m, interval_start__gte = date_from, interval_start__lte=date_to, unit = u).values('interval_start', 'value').order_by('interval_start')

        hour_date = []
        weekly_hour = defaultdict(list)
        weekly_hour_gr = []

        for data in records:
            weekd_cet = make_naive(data['interval_start'], cet)
            hour_date.append({str(weekd_cet)[:13]: data['value']})

        #
        # Sum per hour all values
        #
        for d in hour_date: # you can list as many input dicts as you want here
            for key, value in d.iteritems():
                weekly_hour[key].append(value)

        for key in weekly_hour.keys():
            weekday = int(datetime.strptime(key[:10], '%Y-%m-%d').isoweekday())
            hour = int(str(key)[11:13])
            weekly_hour_gr.append({(weekday-1)*24+hour: sum(item for item in weekly_hour[key])})

        weekly_list = defaultdict(list)
        weekly_res = []
        for d in weekly_hour_gr: # you can list as many input dicts as you want here
            for key, value in d.iteritems():
                weekly_list[key].append(value)


        for key in weekly_list.keys():
            # weekly_res.append({'hour':key, 'value' : sum(item for item in weekly_list[key])/ len(weekly_list[key])})
            weekly_res.append([key, sum(item for item in weekly_list[key])/ len(weekly_list[key])])

        weekly_res = sorted(weekly_res, key=lambda x: x[0])
        # print 'data per weekely hour ==== ', weekly_res

    except:
        return render(request, 'tool/notfound/404.html', {'page': 'Data chart', 'error': '404 Not found'})
    return render(request, 'tool/chart/report-weekly.html', {'records': weekly_res, 'meter': m, 'info':info})


# @login_required(login_url="/login/")
# def chart_json(request, meter, datetime_from, datetime_to):
#     cet = pytz.timezone('CET')
#     date_from = datetime.strptime(datetime_from, "%Y%m%d").date()
#     date_to = datetime.strptime(datetime_to, "%Y%m%d").date()
#     m = Meter.objects.get(meter_id = meter)
#     records = EnergyConsumptionRecord.objects.filter(meter = m, interval_start__gte = date_from, interval_start__lte=date_to).values_list('interval_start', 'value')
#     reg_list = [[make_naive(f, cet), s] for [f, s] in records]
#     records_list = sorted(reg_list, key=lambda x: x[0])
#     # print 'naive = ', reg_list
#     # record_list = [[int(datetime.strptime(str(f)[:16], "%Y-%m-%d %H:%M").strftime('%s')) * 1000, s] for [f, s] in reg_list]
#     # record_list = [['Date.UTC('+str(f.year)+','+str(f.month)+','+str(f.day)+','+str(f.hour)+','+str(f.minute)+')', s] for [f, s] in records_list]
#     record_list = ['[Date.UTC('+str(f.year)+','+str(f.month)+','+str(f.day)+','+str(f.hour)+','+str(f.minute)+'),'+ str(s)+'],' for [f, s] in records_list]
#     record_string = '?([\n'+'\n'.join(record_list)+']);'
#     d = len(record_string)
#     records_string = ''.join([record_string[i] for i in range(len(record_string)) if i  != d-4])
#     return HttpResponse(records_string, content_type='text/javascript;charset=UTF-8')
    # return HttpResponse('?([[Date.UTC(2013,5,2),0.7695],[Date.UTC(2013,5,3),0.7648]])', content_type='text/javascript;charset=UTF-8')
    # return JsonResponse({'records':record_list})

@login_required(login_url="/login/")
def index(request):
    try:
        report_list = EnergyConsumptionReport.objects.order_by('-pk')
    except:
        report_list = []

    title = request.GET.get('title')
    if title:
        report_list = report_list.filter(
        Q(title__icontains = title)
        ).distinct()

    paginator = Paginator(report_list, 10) # Show 10 contacts per page

    page = request.GET.get('page')


    try:
        reports = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        reports = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        reports = paginator.page(paginator.num_pages)

    if paginator.num_pages > 10 :
        # Get the index of the current page
        index = reports.number - 1  # edited to something easier without index
        # This value is maximum index of your pages, so the last page - 1
        max_index = len(paginator.page_range)
        # You want a range of 7, so lets calculate where to slice the list
        start_index = index - 3 if index >= 3 else 0
        end_index = index + 3 if index <= max_index - 3 else max_index
        # My new page range
        reports_range = range(start_index+1,end_index+1)
    else :
        reports_range = paginator.page_range

    return render(request, 'tool/index/index.html', {'reports': reports, 'reports_range':reports_range, 'title':title})

@login_required(login_url="/login/")
def upload_files(request):
    if request.method == 'POST':
        form = EnergyConsumptionFileForm(request.POST, request.FILES)
        if form.is_valid():
            if (form.cleaned_data.get('site') == None):
                # return HttpResponseNotFound('<h1>No Site Selected</h1> <br> <a href="/upload/"><< Return to Uploading files !</a>')
                return render(request, 'tool/notfound/404.html', {'page': 'Upload files', 'error': '404 Not found'})

            files = []
            for f in request.FILES.getlist('data_file'):

                fileName = f.name.replace("(","")
                fileName = fileName.replace(")","")[:-5]
                print fileName
                # s = Site.objects.get_or_create(name = f.name[:18])
                if EnergyConsumptionFile.objects.filter(data_file__icontains = fileName).exists():
                    files.append({'file': f.name, 'color': 'red'})
                    pass
                else :
                    files.append({'file': f.name, 'color': 'green'})
                    instance = EnergyConsumptionFile(data_file = f, site = form.cleaned_data.get('site'))
                    instance.save()
            return render(request, 'tool/after_upload/files.html', {'files': files})
    else:
        form = EnergyConsumptionFileForm()
    return render(request, 'tool/basic_upload/index.html', {'form': form})

@login_required(login_url="/login/")
def upload_reports(request):
    if request.method == 'POST':
        form = EnergyConsumptionReportForm(request.POST)
        if form.is_valid():
            datetime_from = datetime.strptime(str(request.POST['datetime_from'])[:16], '%Y-%m-%d %H:%M')
            datetime_to = datetime.strptime(str(request.POST['datetime_to'])[:16], '%Y-%m-%d %H:%M')
            # print 'unit =====', form.cleaned_data['unit']
            # if str(request.POST['time_peak'])[:5] == '' and str(request.POST['time_peakoff'])[:5] == '':
            #     time_peak = None
            #     time_peakoff = None
            # else :
            #     time_peak = str(request.POST['time_peak'])[:5]
            #     time_peakoff = str(request.POST['time_peakoff'])[:5]
            instance = EnergyConsumptionReport(title = request.POST['title'], meter = form.cleaned_data.get('meter'), datetime_from = datetime_from, datetime_to = datetime_to, unit = form.cleaned_data['unit'])
            instance.save()
            instance.shedules.add(*form.cleaned_data.get('shedules'))
            if 'pfc' in form.cleaned_data.get('meter').site.name.lower():
                instance.produce_pfc_report()
            elif 'cc' in form.cleaned_data.get('meter').site.name.lower():
                instance.produce_cc_report()
            else:
                instance.produce_report()
            return HttpResponseRedirect('/')
    else:
        form = EnergyConsumptionReportForm()
    locations = Location.objects.all()
    return render(request, 'tool/report/upload.html', {'form': form, 'locations':locations})

@login_required(login_url="/login/")
def edit_reports(request, id):
    post = get_object_or_404(EnergyConsumptionReport, id=id)
    if request.method == "POST":
        form = EnergyConsumptionReportForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            print 'post: ', post
            # print form.cleaned_data.get('unit')
            post.save()
            form.save_m2m()
            if 'pfc' in form.cleaned_data.get('meter').site.name.lower():
                post.produce_pfc_report()
            elif 'cc' in form.cleaned_data.get('meter').site.name.lower():
                post.produce_cc_report()
            else :
                post.produce_report()
            return HttpResponseRedirect('/')
    else:
        form = EnergyConsumptionReportForm(instance=post)
    return render(request, 'tool/report/edit.html', {'form': form, 'id': id})

@login_required(login_url="/login/")
def delete_report(request, id):
    new_to_delete = get_object_or_404(EnergyConsumptionReport, id=id)
    new_to_delete.delete()
    return HttpResponseRedirect("/")

@login_required(login_url="/login/")
def upload_meter(request):
    if request.method == 'POST':
        form = MeterForm(request.POST)
        if form.is_valid():
            instance = Meter(meter_id = request.POST['meter_id'], site = form.cleaned_data.get('site'))
            instance.save()
            return HttpResponseRedirect('/')
    else:
        form = MeterForm()
    return render(request, 'tool/meter/upload.html', {'form': form})




@login_required(login_url="/login/")
def sites(request):
    try:
        sites_list = Site.objects.order_by('-pk')
    except:
        sites_list = []

    name = request.GET.get('name')
    if name:
        sites_list = sites_list.filter(
        Q(name__icontains = name)
        ).distinct()

    paginator = Paginator(sites_list, 10) # Show 10 contacts per page

    page = request.GET.get('page')


    try:
        sites = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        sites = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        sites = paginator.page(paginator.num_pages)

    if paginator.num_pages > 10 :
        # Get the index of the current page
        index = sites.number - 1  # edited to something easier without index
        # This value is maximum index of your pages, so the last page - 1
        max_index = len(paginator.page_range)
        # You want a range of 7, so lets calculate where to slice the list
        start_index = index - 3 if index >= 3 else 0
        end_index = index + 3 if index <= max_index - 3 else max_index
        # My new page range
        sites_range = range(start_index+1,end_index+1)
    else :
        sites_range = paginator.page_range


    return render(request, 'tool/site/sites.html', {'sites': sites, 'sites_range':sites_range, 'name':name})

@login_required(login_url="/login/")
def add_site(request):
    if request.method == 'POST':
        form = SiteForm(request.POST)
        if form.is_valid():
            instance = Site(name = request.POST['name'].replace(' ','_'), location = form.cleaned_data.get('location'), company = form.cleaned_data.get('company'))
            instance.save()
            return HttpResponseRedirect('/sites/')
    else:
        form = SiteForm()
    return render(request, 'tool/site/add.html', {'form': form})

@login_required(login_url="/login/")
def edit_site(request, id):
    post = get_object_or_404(Site, id=id)
    if request.method == 'POST':
        form = SiteForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            print 'post: ', post
            post.save()
            return HttpResponseRedirect('/sites/')
    else:
        form = SiteForm(instance=post)
    return render(request, 'tool/site/edit.html', {'form': form, 'id': id})

@login_required(login_url="/login/")
def delete_site(request, id):
    new_to_delete = get_object_or_404(Site, id=id)
    new_to_delete.delete()
    return HttpResponseRedirect("/sites/")



@login_required(login_url="/login/")
def add_company(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            instance = Company(name = request.POST['name'])
            instance.save()
            return HttpResponseRedirect('/companies/')
    else:
        form = CompanyForm()
    return render(request, 'tool/company/add.html', {'form': form})


@login_required(login_url="/login/")
def companies(request):
    try:
        company_list = Company.objects.order_by('-pk')
    except:
        company_list = []

    name = request.GET.get('name')
    if name:
        company_list = company_list.filter(
        Q(name__icontains = name)
        ).distinct()

    paginator = Paginator(company_list, 10) # Show 10 contacts per page

    page = request.GET.get('page')


    try:
        companies = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        companies = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        companies = paginator.page(paginator.num_pages)

    if paginator.num_pages > 10 :
        # Get the index of the current page
        index = companies.number - 1  # edited to something easier without index
        # This value is maximum index of your pages, so the last page - 1
        max_index = len(paginator.page_range)
        # You want a range of 7, so lets calculate where to slice the list
        start_index = index - 3 if index >= 3 else 0
        end_index = index + 3 if index <= max_index - 3 else max_index
        # My new page range
        companies_range = range(start_index+1,end_index+1)
    else :
        companies_range = paginator.page_range


    return render(request, 'tool/company/companies.html', {'companies': companies, 'companies_range':companies_range, 'name':name})

@login_required(login_url="/login/")
def edit_company(request, id):
    post = get_object_or_404(Company, id=id)
    if request.method == 'POST':
        form = CompanyForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            print 'post: ', post
            post.save()
            return HttpResponseRedirect('/companies/')
    else:
        form = CompanyForm(instance=post)
    return render(request, 'tool/company/edit.html', {'form': form, 'id': id})

@login_required(login_url="/login/")
def delete_company(request, id):
    new_to_delete = get_object_or_404(Company, id=id)
    new_to_delete.delete()
    return HttpResponseRedirect("/companies/")


@login_required(login_url="/login/")
def files(request):

    try:
        companies = Company.objects.order_by('-pk')
    except:
        companies = []

    try:
        meters = Meter.objects.order_by('-pk')
    except:
        meters = []

    try:
        files_list = EnergyConsumptionFile.objects.order_by('-pk')
    except:
        files_list = []

    sort = request.GET.get('sort')

    if sort:
        comp = Company.objects.order_by('-pk').filter(name__icontains = sort)[0]
        s_id = Site.objects.order_by('-pk').filter(company = comp.id)

        data_list = []
        for s in s_id:
            data_list.append(int(s.id))

        files_list = files_list.filter(
        Q(site__in = data_list)
        ).distinct()

    meter = request.GET.get('meter')

    if meter:
        print 'meter = ', meter.split()[4]
        print 'm = ', meter.split()[3]

        try:
            sit = Site.objects.get(name = str(meter.split()[4]))
            print sit
        except Site.DoesNotExist:
            return render(request, 'tool/notfound/404.html', {'page': 'No such site', 'error': '404'})
            # return HttpResponseNotFound('<h1>No such files</h1> <br> <a href="/files/"><< Return to files page !</a>')

        files_list = files_list.filter(
        Q(site = sit.id)
        ).distinct()

    files = request.GET.getlist('files')

    if files:
        f_list = []
        for f in files:
            f_list.append(int(f))
        print 'f ===  ', f_list

        for fl in f_list:
            new_to_delete = get_object_or_404(EnergyConsumptionFile, id=fl)
            new_to_delete.delete()
        return HttpResponseRedirect("/files/")


    paginator = Paginator(files_list, 12) # Show 20 contacts per page

    page = request.GET.get('page')

    try:
        files = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        files = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        files = paginator.page(paginator.num_pages)

    if paginator.num_pages > 10 :
        # Get the index of the current page
        index = files.number - 1  # edited to something easier without index
        # This value is maximum index of your pages, so the last page - 1
        max_index = len(paginator.page_range)
        # You want a range of 7, so lets calculate where to slice the list
        start_index = index - 3 if index >= 3 else 0
        end_index = index + 3 if index <= max_index - 3 else max_index
        # My new page range
        files_range = range(start_index+1,end_index+1)
    else :
        files_range = paginator.page_range



    return render(request, 'tool/files/files.html', {'files': files, 'files_range': files_range, 'companies': companies, 'meters' : meters})

@login_required(login_url="/login/")
def delete_file(request, id):
    new_to_delete = get_object_or_404(EnergyConsumptionFile, id=id)
    new_to_delete.delete()
    return HttpResponseRedirect("/files/")

@login_required(login_url="/login/")
def shedules(request):
    try:
        shedules_list = Shedule.objects.order_by('-pk')
    except:
        shedules_list = []

    name = request.GET.get('name')
    if name:
        shedules_list = shedules_list.filter(
        Q(title__icontains = name)
        ).distinct()

    paginator = Paginator(shedules_list, 10) # Show 10 contacts per page

    page = request.GET.get('page')


    try:
        schedules = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        schedules = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        schedules = paginator.page(paginator.num_pages)

    if paginator.num_pages > 10 :
        # Get the index of the current page
        index = shedules.number - 1  # edited to something easier without index
        # This value is maximum index of your pages, so the last page - 1
        max_index = len(paginator.page_range)
        # You want a range of 7, so lets calculate where to slice the list
        start_index = index - 3 if index >= 3 else 0
        end_index = index + 3 if index <= max_index - 3 else max_index
        # My new page range
        shedules_range = range(start_index+1,end_index+1)
    else :
        shedules_range = paginator.page_range


    return render(request, 'tool/shedule/shedules.html', {'schedules': schedules, 'shedules_range':shedules_range, 'name':name})

@login_required(login_url="/login/")
def add_shedule(request):
    if request.method == 'POST':
        form = SheduleForm(request.POST)
        if form.is_valid():
            print form.cleaned_data['country']
            print form.cleaned_data['hours']
            print form.cleaned_data['holiday']
            print form.cleaned_data['weekend']
            instance = Shedule(title = request.POST['title'], country = form.cleaned_data['country'], holiday = form.cleaned_data['holiday'], off_holiday = form.cleaned_data['off_holiday'], all_holidays = form.cleaned_data['all_holidays'], weekend = form.cleaned_data['weekend'])
            instance.save()
            instance.hours.add(*form.cleaned_data['hours'])
            instance.months.add(*form.cleaned_data['months'])
            instance.weekdays.add(*form.cleaned_data['weekdays'])
            instance.weekend_days.add(*form.cleaned_data['weekend_days'])
            return HttpResponseRedirect('/schedules/')
    else:
        form = SheduleForm()
    return render(request, 'tool/shedule/add.html', {'form': form})

@login_required(login_url="/login/")
def edit_shedule(request, id):
    post = get_object_or_404(Shedule, id=id)
    if request.method == "POST":
        print request.POST.get('holiday')
        form = SheduleForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            print 'post: ', post
            post.save()
            form.save_m2m()
            return HttpResponseRedirect('/schedules/')
    else:
        form = SheduleForm(instance=post)
    return render(request, 'tool/shedule/edit.html', {'form': form, 'id': id})

@login_required(login_url="/login/")
def delete_schedule(request, id):
    new_to_delete = get_object_or_404(Shedule, id=id)
    new_to_delete.delete()
    return HttpResponseRedirect("/schedules/")

## locations

@login_required(login_url="/login/")
def locations(request):
    try:
        locations_list = Location.objects.order_by('-pk')
    except:
        locations_list = []

    name = request.GET.get('name')
    if name:
        locations_list = locations_list.filter(
        Q(title__icontains = name)
        ).distinct()

    paginator = Paginator(locations_list, 10) # Show 10 contacts per page

    page = request.GET.get('page')


    try:
        locations = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        locations = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        locations = paginator.page(paginator.num_pages)

    if paginator.num_pages > 10 :
        # Get the index of the current page
        index = locations.number - 1  # edited to something easier without index
        # This value is maximum index of your pages, so the last page - 1
        max_index = len(paginator.page_range)
        # You want a range of 7, so lets calculate where to slice the list
        start_index = index - 3 if index >= 3 else 0
        end_index = index + 3 if index <= max_index - 3 else max_index
        # My new page range
        locations_range = range(start_index+1,end_index+1)
    else :
        locations_range = paginator.page_range


    return render(request, 'tool/location/locations.html', {'locations': locations, 'locations_range':locations_range, 'name':name})

@login_required(login_url="/login/")
def add_location(request):
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            instance = Location(name = request.POST['name'], country = form.cleaned_data['country'])
            instance.save()
            instance.holidays.add(*form.cleaned_data['holidays'])
            return HttpResponseRedirect('/locations/')
    else:
        form = LocationForm()
    return render(request, 'tool/location/add.html', {'form': form})

@login_required(login_url="/login/")
def edit_location(request, id):
    post = get_object_or_404(Location, id=id)
    if request.method == "POST":
        # print request.POST.get('holidays')
        form = LocationForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            print 'post: ', post
            post.save()
            form.save_m2m()
            return HttpResponseRedirect('/locations/')
    else:
        form = LocationForm(instance=post)
    return render(request, 'tool/location/edit.html', {'form': form, 'id': id})


## Holidays

@login_required(login_url="/login/")
def holidays(request):
    try:
        holidays_list = Holiday.objects.order_by('-pk')
    except:
        holidays_list = []

    name = request.GET.get('name')
    if name:
        holidays_list = holidays_list.filter(
        Q(title__icontains = name)
        ).distinct()

    paginator = Paginator(holidays_list, 10) # Show 10 contacts per page

    page = request.GET.get('page')


    try:
        holidays = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        holidays = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        holidays = paginator.page(paginator.num_pages)

    if paginator.num_pages > 10 :
        # Get the index of the current page
        index = holidays.number - 1  # edited to something easier without index
        # This value is maximum index of your pages, so the last page - 1
        max_index = len(paginator.page_range)
        # You want a range of 7, so lets calculate where to slice the list
        start_index = index - 3 if index >= 3 else 0
        end_index = index + 3 if index <= max_index - 3 else max_index
        # My new page range
        holidays_range = range(start_index+1,end_index+1)
    else :
        holidays_range = paginator.page_range


    return render(request, 'tool/holiday/holidays.html', {'holidays': holidays, 'holidays_range':holidays_range, 'name':name})

@login_required(login_url="/login/")
def add_holiday(request):
    if request.method == 'POST':
        form = HolidayForm(request.POST)
        if form.is_valid():
            holiday_date = datetime.strptime(str(request.POST['date'])[:16], '%d/%m/%Y')
            instance = Holiday(title = request.POST['title'], date = holiday_date, country = form.cleaned_data['country'])
            instance.save()
            return HttpResponseRedirect('/holidays/')
    else:
        form = HolidayForm()
    return render(request, 'tool/holiday/add.html', {'form': form})

@login_required(login_url="/login/")
def edit_holiday(request, id):
    post = get_object_or_404(Holiday, id=id)
    if request.method == "POST":
        # print request.POST.get('holidays')
        form = HolidayForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            print 'post: ', post
            post.save()
            form.save_m2m()
            return HttpResponseRedirect('/holidays/')
    else:
        form = HolidayForm(instance=post)
    return render(request, 'tool/holiday/edit.html', {'form': form, 'id': id})

@login_required(login_url="/login/")
def delete_holiday(request, id):
    new_to_delete = get_object_or_404(Holiday, id=id)
    new_to_delete.delete()
    return HttpResponseRedirect("/holidays/")


### Budget

@login_required(login_url="/login/")
def budget_reports(request):
    try:
        report_list = BudgetReport.objects.order_by('-pk')
    except:
        report_list = []

    title = request.GET.get('title')
    if title:
        report_list = report_list.filter(
        Q(title__icontains = title)
        ).distinct()

    paginator = Paginator(report_list, 10) # Show 10 contacts per page

    page = request.GET.get('page')


    try:
        reports = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        reports = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        reports = paginator.page(paginator.num_pages)

    if paginator.num_pages > 10 :
        # Get the index of the current page
        index = reports.number - 1  # edited to something easier without index
        # This value is maximum index of your pages, so the last page - 1
        max_index = len(paginator.page_range)
        # You want a range of 7, so lets calculate where to slice the list
        start_index = index - 3 if index >= 3 else 0
        end_index = index + 3 if index <= max_index - 3 else max_index
        # My new page range
        reports_range = range(start_index+1, end_index+1)
    else :
        reports_range = paginator.page_range


    return render(request, 'tool/budget-report/index.html', {'reports': reports, 'reports_range':reports_range, 'title':title})


@login_required(login_url="/login/")
def upload_reports_budget(request):
    if request.method == 'POST':
        form = BudgetReportForm(request.POST)
        if form.is_valid():
            datetime_from = datetime.strptime(str(request.POST['datetime_from'])[:16], '%Y-%m-%d %H:%M')
            datetime_to = datetime.strptime(str(request.POST['datetime_to'])[:16], '%Y-%m-%d %H:%M')
            self_unit = request.POST['unit'][:request.POST['unit'].index("/")]
            pfc_met = Meter.objects.get(id = int(request.POST['pfc']))
            print pfc_met
            instance = BudgetReport(title = request.POST['title'], budget = form.cleaned_data.get('budget'), datetime_from = datetime_from, datetime_to = datetime_to, unit = request.POST['unit'], pfc = int(request.POST['pfc']), self_unit = self_unit)
            instance.save()
            instance.shedules.add(*form.cleaned_data.get('shedules'))
            instance.produce_budget_report()
            return HttpResponseRedirect('/budgets/')
            # if EnergyConsumptionRecord.objects.filter(meter = form.cleaned_data.get('budget'), interval_start__gte = datetime_from, interval_start__lte = datetime_to).exists() and EnergyConsumptionRecord.objects.filter(meter = pfc_met, interval_start__gte = datetime_from, interval_start__lte = datetime_to, unit = self_unit).exists() :
            #     instance = BudgetReport(title = request.POST['title'], budget = form.cleaned_data.get('budget'), datetime_from = datetime_from, datetime_to = datetime_to, unit = request.POST['unit'], pfc = int(request.POST['pfc']), self_unit = self_unit)
            #     instance.save()
            #     instance.shedules.add(*form.cleaned_data.get('shedules'))
            #     instance.produce_budget_report()
            #     return HttpResponseRedirect('/budgets/')
            # else:
            #     return render(request, 'tool/notfound/404.html', {'page': 'No such data in database', 'error': '404'})
    else:
        form = BudgetReportForm()
    locations = Location.objects.all()
    meters = Meter.objects.filter(meter_id__icontains = 'pfc')
    return render(request, 'tool/budget-report/upload.html', {'form': form, 'locations':locations, 'meters': meters})

@login_required(login_url="/login/")
def edit_reports_budget(request, id):
    post = get_object_or_404(BudgetReport, id=id)
    if request.method == "POST":
        form = BudgetReportForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            print 'post: ', post
            post.save()
            form.save_m2m()
            post.produce_budget_report()
            return HttpResponseRedirect('/budgets/')
    else:
        form = BudgetReportForm(instance=post)
    meters = Meter.objects.filter(meter_id__icontains = 'pfc')
    return render(request, 'tool/budget-report/edit.html', {'form': form, 'id': id, 'meters':meters, 'unit_selected':form['pfc'].value})

@login_required(login_url="/login/")
def delete_report_budget(request, id):
    new_to_delete = get_object_or_404(BudgetReport, id=id)
    new_to_delete.delete()
    return HttpResponseRedirect("/budgets/")


### Sum meters

@login_required(login_url="/login/")
def meters_sum(request):
    try:
        report_list = SumDiffReport.objects.order_by('-pk')
    except:
        report_list = []

    title = request.GET.get('title')
    if title:
        report_list = report_list.filter(
        Q(title__icontains = title)
        ).distinct()

    paginator = Paginator(report_list, 10) # Show 10 contacts per page

    page = request.GET.get('page')


    try:
        reports = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        reports = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        reports = paginator.page(paginator.num_pages)

    if paginator.num_pages > 10 :
        # Get the index of the current page
        index = reports.number - 1  # edited to something easier without index
        # This value is maximum index of your pages, so the last page - 1
        max_index = len(paginator.page_range)
        # You want a range of 7, so lets calculate where to slice the list
        start_index = index - 3 if index >= 3 else 0
        end_index = index + 3 if index <= max_index - 3 else max_index
        # My new page range
        reports_range = range(start_index+1,end_index+1)
    else :
        reports_range = paginator.page_range


    return render(request, 'tool/sum-diff-report/index.html', {'reports': reports, 'reports_range':reports_range, 'title':title})

@login_required(login_url="/login/")
def upload_meters_sum(request):
    if request.method == 'POST':
        form = SumDiffReportForm(request.POST)
        if form.is_valid():
            print 'meters =', form.cleaned_data.get('meters')
            diff_bool = False
            if request.POST['diff_bool'] == 'True':
                diff_bool = True
            diff_cc = []
            if request.POST['diff'] == '--':
                diff_cc = 0
            else:
                diff_cc = int(request.POST['diff'])
            datetime_from = datetime.strptime(str(request.POST['datetime_from'])[:16], '%Y-%m-%d %H:%M')
            datetime_to = datetime.strptime(str(request.POST['datetime_to'])[:16], '%Y-%m-%d %H:%M')
            instance = SumDiffReport(title = request.POST['title'], datetime_from = datetime_from, datetime_to = datetime_to, diff_bool = diff_bool, diff_cc = diff_cc)
            instance.save()
            instance.shedules.add(*form.cleaned_data.get('shedules'))
            instance.meters.add(*form.cleaned_data.get('meters'))
            instance.produce_sum_diff_report()
            return HttpResponseRedirect('/sum/')
    else:
        form = SumDiffReportForm()
    locations = Location.objects.all()
    meters = Meter.objects.filter(meter_id__icontains = 'cc')
    return render(request, 'tool/sum-diff-report/upload.html', {'form': form, 'locations':locations, 'meters':meters})

@login_required(login_url="/login/")
def edit_meters_sum(request, id):
    post = get_object_or_404(SumDiffReport, id=id)
    if request.method == "POST":
        form = SumDiffReportForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            if request.POST.get('diff') == '--':
                post.diff_cc = 0
            else:
                post.diff_cc = int(request.POST.get('diff'))
            # post.diff_cc = request.POST.get('diff')
            print 'post: ', post.diff_cc
            post.save()
            form.save_m2m()
            post.produce_sum_diff_report()
            return HttpResponseRedirect('/sum/')
    else:
        form = SumDiffReportForm(instance=post)
    meters = Meter.objects.filter(meter_id__icontains = 'cc')
    sumd = SumDiffReport.objects.get(id = id)
    return render(request, 'tool/sum-diff-report/edit.html', {'form': form, 'id': id, 'meters':meters, 'unit_selected':sumd.diff_cc})

@login_required(login_url="/login/")
def delete_meters_sum(request, id):
    new_to_delete = get_object_or_404(SumDiffReport, id=id)
    new_to_delete.delete()
    return HttpResponseRedirect("/sum/")


# Translation Records to a specifc year

@login_required(login_url="/login/")
def translations(request):
    try:
        translations_list = TranslationRecords.objects.order_by('-pk')
    except:
        translations_list = []

    title = request.GET.get('title')
    if title:
        translations_list = translations_list.filter(
        Q(title__icontains = title)
        ).distinct()

    paginator = Paginator(translations_list, 10) # Show 10 contacts per page

    page = request.GET.get('page')


    try:
        translations = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        translations = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        translations = paginator.page(paginator.num_pages)

    if paginator.num_pages > 10 :
        # Get the index of the current page
        index = translations.number - 1  # edited to something easier without index
        # This value is maximum index of your pages, so the last page - 1
        max_index = len(paginator.page_range)
        # You want a range of 7, so lets calculate where to slice the list
        start_index = index - 3 if index >= 3 else 0
        end_index = index + 3 if index <= max_index - 3 else max_index
        # My new page range
        translations_range = range(start_index+1,end_index+1)
    else :
        translations_range = paginator.page_range


    return render(request, 'tool/translation/translations.html', {'translations': translations, 'translations_range':translations_range, 'title':title})


@login_required(login_url="/login/")
def upload_translation(request):
    if request.method == 'POST':
        form = TranslationRecordsForm(request.POST)
        if form.is_valid():
            if EnergyConsumptionRecord.objects.filter(meter = form.cleaned_data.get('translation_meter')) > 100 :
                instance = TranslationRecords(title = request.POST['title'], translation_meter = form.cleaned_data.get('translation_meter'))
                # instance = TranslationRecords(title = request.POST['title'], translation_meter = form.cleaned_data.get('translation_meter'), year = request.POST['year'], translated_year = request.POST['translated_year'])
                instance.save()
            else:
                return render(request, 'tool/notfound/404.html', {'page': 'There is no such data in database !!!', 'error': '404'})
            return HttpResponseRedirect('/translations/')
    else:
        form = TranslationRecordsForm()
    return render(request, 'tool/translation/upload.html', {'form': form})


@login_required(login_url="/login/")
def edit_translation(request, id):
    post = get_object_or_404(TranslationRecords, id=id)
    if request.method == "POST":
        form = TranslationRecordsForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            print 'post: ', post
            post.save()
            return HttpResponseRedirect('/translations/')
    else:
        form = TranslationRecordsForm(instance=post)
    return render(request, 'tool/translation/edit.html', {'form': form, 'id': id})


@login_required(login_url="/login/")
def delete_translation(request, id):
    try:
        tr = TranslationRecords.objects.get(id=id)
        year_delete = EnergyConsumptionRecord.objects.filter(interval_start__year = tr.year)
        year_delete.delete()
    except:
        print 'no data for this year'
    new_to_delete = get_object_or_404(TranslationRecords, id=id)
    new_to_delete.delete()
    return HttpResponseRedirect("/budgets/")
