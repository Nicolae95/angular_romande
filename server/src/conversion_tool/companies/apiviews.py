from django.shortcuts import *
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from datetime import datetime, timedelta
from pytz import country_timezones
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpRequest
from rest_framework import status
from .models import *
from core.models import *
from .forms import *
from .serializers import *
from core.models import *
from translations.models import *
from offers.models import *
from offers.serializers import *
from django.db.models import Sum



class YearsBySiteListViewSet(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)


    def get(self, request, pk, format=None):
        try:
            meter = Meter.objects.get(site_id=pk, meter_sum=True)
            site_year = Site.objects.get(id=int(pk)).year
            years = []
            trecords = TranslationRecord.objects.filter(meter=meter).values_list('interval_start', flat=True)
            for tr in list(trecords):
                years.append(int(tr.year))
            years.append(site_year)
            years = sorted(reduce(lambda r, v: v in r and r or r + [v], years, []))
            # print 'start years', years
            try:
                off_sign = Offer.objects.get(cc=meter, lissage=True, offer_status='signee').years_list
            except:
                off_sign = []
            try:
                off = Offer.objects.get(cc=meter, lissage=False,  offer_status='signee').years_list
            except:
                off = []
            try:
                off_signer = Offer.objects.get(cc=meter, offer_status='signer').years_list
            except:
                off_signer = []
            all_years = off_sign + off
            seen_set = set()
            duplicate_set = set(x for x in all_years if x in seen_set or seen_set.add(x))
            duplicate_set = list(duplicate_set)
            # print duplicate_set, years, off_signer
            # print 'years = ', years
            years_list = []
            for year in years:
                # print year
                if str(year) in duplicate_set:
                    # print 'dub = ', year
                    years.remove(year)
                else:
                    years_list.append(year)
            # try:
            #     years_list.remove(2017)
            #     years_list.remove(2018)
            # except:
            #     print('no years')
            years_result = []
            for y in years_list:
                if int(y) > datetime.now().year:
                    years_result.append(y)
        except:
            return Response(OrderedDict([('years', [])]),  status=status.HTTP_404_NOT_FOUND)
        return Response(OrderedDict([('years', sorted(years_result))]), status=status.HTTP_200_OK)



class DashboardBySiteView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, site, format=None):
        cet = pytz.timezone('utc')
        try:
            meter = Meter.objects.filter(site_id=int(site), meter_sum=True)
            cyear = Site.objects.get(id=int(site)).year
            years = sorted(range(cyear, cyear+7), reverse=True)
            print years
        except:
            return Response(status=status.HTTP_204_NO_CONTENT)
        year = self.request.query_params.get('year', None)
        q = Q()
        if year != None:
            if len(year) == 4 and year.isdigit():
                q &= Q(created__year = int(year))
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)

        months = MonthRecord.objects.filter(meter=meter, year=int(year)).values('month', 'schedule__title', 'value')
        seasons = SeasonRecord.objects.filter(meter=meter, year=int(year)).values('season', 'schedule__title', 'value')
        print 'seasons = ', seasons
        try:
            headges = HeadgeRecord.objects.filter(meter=meter, year=int(year)).values('schedule__title', 'value')
        except:
            headges = []
        from django.db.models import Count, Sum
        from collections import defaultdict
        shedule_sum = defaultdict()
        shedules = MonthRecord.objects.filter(meter=meter, year=int(year)).values_list('schedule__title', flat=True).distinct()
        shedules = reduce(lambda r, v: v in r and r or r + [v], shedules, [])
        shedule_sum['Total'] = MonthRecord.objects.filter(meter=meter, year=int(year)).aggregate(Sum('value'))
        hour = 8
        hourlast = 20
        hours = []
        hourslast = []
        for shedule in shedules:
            # hour = sorted(Shedule.objects.get(title=shedule).hours.all().values_list('value', flat=True))[0]
            shedule_sum[shedule] = MonthRecord.objects.filter(meter=meter, year=int(year), schedule__title=shedule).aggregate(Sum('value'))
            days = (list(Shedule.objects.get(title=shedule).weekdays.all().values_list('day', flat=True)) +
                    list(Shedule.objects.get(title=shedule).weekend_days.all().values_list('day', flat=True)))
            try:
                for h in map(lambda x: (x-1)*24+hour, sorted(days)):
                    hours.append([h, HeadgeRecord.objects.get(meter=meter, year=int(year), schedule__title=shedule).value])
                for hl in map(lambda x: (x-1)*24+hourlast, sorted(days)):
                    hours.append([hl, HeadgeRecord.objects.get(meter=meter, year=int(year), schedule__title=shedule).value])
            except:
                hours = []

        # print hours
        # print 'sum = ', shedule_sum

        totald = []
        total = defaultdict(int)
        diagram = []
        for d in list(months):
            total[d['month']] += d['value']
            # diagram.append([d['month'], d['value']])
            # total.append({'month': d['month'], 'value':d['value']})

        for key in total:
            totald.append({'month': key, 'value': total[key]})
            diagram.append([key, (total[key]/float(1000))])
        
        try:
            hours = list(map(lambda x: [x[0], x[1]/float(1000)], hours))
            hours = sorted(hours, key=lambda x:  (x[0], x[1]))
            odd_numbers = [y for x,y in enumerate(hours) if x%2 != 0]
            even_numbers = [y for x,y in enumerate(hours) if x%2 == 0]
            # print 'odd = ', odd_numbers , len(odd_numbers)
            # print 'even = ', even_numbers, len(even_numbers)
            hdata = []
            for index, value in enumerate(odd_numbers):
                if index%2 == 0:
                    # hdata.append([even_numbers[index], odd_numbers[index]])
                    hdata.append(even_numbers[index])
                    hdata.append(odd_numbers[index])
                else:
                    # hdata.append([odd_numbers[index], even_numbers[index]])
                    hdata.append(odd_numbers[index])
                    hdata.append(even_numbers[index])
            # print hdata
        except:
            hdata = []

        months_list = []
        # print 'months', months_list
        for month in months:
            months_list.append(
                # {'value': "{:,}".format(round(month['value'], 2)).replace(",", "'"), 'schedule__title': month['schedule__title'], 'month':  month['month']}
                {'value': "{:,}".format(int(round(month['value']))).replace(",", "'"), 'schedule__title': month['schedule__title'], 'month':  month['month']}
            )
        
        total_list = []
        for mont in totald:
            print mont
            total_list.append(
                {'value': "{:,}".format(int(round(mont['value']))).replace(
                    ",", "'"), 'month': mont['month']}
            )
        
        shedule_list = defaultdict()
        for mt in shedule_sum:
            shedule_list[mt] = {'value__sum': "{:,}".format(
                int(round(shedule_sum[mt]['value__sum']))).replace(",", "'")
            }
            # print 'mt = ', mt, shedule_sum[mt]
        try:
            form = Site.objects.get(id=int(site)).format_donnees
            pond = EnergyConsumptionRecord.objects.filter(meter=meter)[0].from_file
            if not pond:
                form = 'pondere'
        except:
            form = '--'

        print shedule_list

        mweekly = []
        weekly = WeeklyRecord.objects.filter(meter=meter, year=int(year)).values_list('hour', 'value')
        for week in weekly:
            mweekly.append([week[0], week[1]/float(1000)])
            # mweekly.append([week[0], week[1]])

        return Response(OrderedDict([('years', years),
                                     ('interval', form),
                                     ('months_value', months_list),
                                     ('months_total', shedule_list),
                                     ('months', total_list),
                                     ('months_diagram', diagram),
                                     ('season_value', seasons),
                                     ('weekly_value', mweekly),
                                     ('headges', headges),
                                     ('hedges_diagram', hdata),
                                    ]), status=status.HTTP_200_OK)


class SiteProfilesListViewSet(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        name = self.request.query_params.get('name', None)
        year = self.request.query_params.get('year', None)
        nr = self.request.query_params.get('nr', None)
        pag = self.request.query_params.get('pag', 1)
        last = 0
        first = 0
        if nr:
            per_page = int(nr)
        else:
            per_page = 10
        q = Q()
        if name:
            q &= Q(name__icontains = str(name))
        if year:
            q &= Q(created__year = int(year))

        snippets = Site.objects.filter(q).order_by('-pk')
        if int(len(snippets)) % per_page == 0:
            leng = len(snippets)/per_page
        else :
            leng = len(snippets)/per_page + 1
        if pag == leng:
            first = int(len(snippets)/per_page)*per_page
            last = len(snippets)
        else:
            if int(pag) == 1 :
                first = 0
                last = per_page
            else :
                last = int(pag) * per_page
                first = last - per_page
        print first, last
        serializer = SiteSerializer(snippets[first:last], context={"request": request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # def post(self, request, format=None):
    #     serializer = SiteEditSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SiteByIdView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        snippet = get_object_or_404(Site, id=pk)
        serializer = SiteSerializer(snippet)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        snippet = get_object_or_404(Site, id=pk)
        serializer = SiteEditSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        # print Offer.objects.filter(cc_company_site)
        snippet = get_object_or_404(Site, id=pk)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SiteFilterByCompanyView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        name = self.request.query_params.get('name', None)
        year = self.request.query_params.get('year', None)
        nr = self.request.query_params.get('nr', None)
        pag = self.request.query_params.get('pag', 1)
        last = 0
        first = 0
        q = Q()
        if name:
            q &= Q(name__icontains = str(name))
        if year:
            if len(year) == 4 and year.isdigit():
                q &= Q(created__year = year)
        snippets = Site.objects.filter(company_id=pk).filter(q).order_by('-pk')
        if nr:
            per_page = int(nr)
        else:
            per_page = 10
        if int(len(snippets)) % per_page == 0:
            leng = len(snippets)/per_page
        else :
            leng = len(snippets)/per_page + 1
        if pag == leng:
            first = int(len(snippets)/per_page)*per_page
            last = len(snippets)
        else:
            if int(pag) == 1 :
                first = 0
                last = per_page
            else :
                last = int(pag) * per_page
                first = last - per_page
        print first, last
        serializer = SiteEditSerializer(snippets[first:last], context={"request": request}, many=True)
        return Response(OrderedDict([('pages', leng),
                                     ('pag', int(pag)),
                                     ('result', serializer.data)]),
                        status=status.HTTP_200_OK)


class SiteByCompanyView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        snippets = Site.objects.filter(company_id=pk)
        serializer = SiteEditSerializer(snippets, context={"request": request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SiteVolumeView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        cet = pytz.timezone('utc')
        year= datetime.now().year-1
        try:
            meter = Meter.objects.get(meter_sum=True, site_id=pk)
        except:
            return Response(status=status.HTTP_204_NO_CONTENT)
        data_from = cet.localize(datetime(int(year), 01, 01, 0, 0), is_dst=None)
        data_to = cet.localize(datetime(int(year), 12, 31, 23, 59), is_dst=None)
        records = EnergyConsumptionRecord.objects.filter(meter=meter).aggregate(total_value=Sum('value'))
        # result = {'total_value': int(round(records['total_value']))}
        result = {'total_value': "{:,}".format(int(round(records['total_value']))).replace(",", "'")}
        return Response(result, status=status.HTTP_200_OK)


class CCVolumeView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        print pk
        cet = pytz.timezone('utc')
        year = datetime.now().year-1
        try:
            meter = Meter.objects.get(meter_sum=True, id=pk)
            print meter
        except:
            return Response(status=status.HTTP_204_NO_CONTENT)
        data_from = cet.localize(datetime(int(year), 01, 01, 0, 0), is_dst=None)
        data_to = cet.localize(datetime(int(year), 12, 31, 23, 59), is_dst=None)
        records = EnergyConsumptionRecord.objects.filter(
            meter=meter).aggregate(total_value=Sum('value'))
        result = {'total_value': "{:,}".format(int(round(records['total_value']))).replace(",", "'"), 'site': meter.site.name}
        return Response(result, status=status.HTTP_200_OK)


class CompanyListViewSet(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        snippets = Company.objects.all()
        serializer = CompanySerializer(snippets, context={"request": request}, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        # meters = request.data['podsRows']
        # request.data['func'] = request.data['type']
        # del request.data['type']
        serializer = CompanySerializer(data=request.data)
        if serializer.is_valid():
            print serializer
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompanyPaginationListViewSet(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        pag = self.request.query_params.get('pag', 1)
        nr = self.request.query_params.get('nr', None)
        name = self.request.query_params.get('name', None)
        if not pag:
            pag = 1
        
        last = 0
        first = 0
        q = Q()
        if name:
            q &= Q(Q(name__icontains=name) | Q(surname__icontains=name)
                                           | Q(nom_entrepise__icontains=name))
        snippets = Company.objects.filter(q).order_by('-pk')
        
        if nr:
            per_page = int(nr)
        else:
            per_page = 10
        
        if int(len(snippets)) % per_page == 0:
            leng = len(snippets)/per_page
        else :
            leng = len(snippets)/per_page + 1
        if pag == leng:
            first = int(len(snippets)/per_page)*per_page
            last = len(snippets)
        else:
            if int(pag) == 1 :
                first = 0
                last = per_page
            else :
                last = int(pag) * per_page
                first = last - per_page
        print first, last
        serializer = CompanySerializer(snippets[first:last], context={"request": request}, many=True)
        return Response(OrderedDict([('pages', leng),
                                     ('pag', int(pag)),
                                     ('result', serializer.data)]),
                        status=status.HTTP_200_OK)


class CompanyByIdView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        snippet = get_object_or_404(Company, pk=pk)
        serializer = CompanySerializer(snippet)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        snippet = get_object_or_404(Company, pk=pk)
        serializer = CompanySerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        snippet = get_object_or_404(Company, pk=pk)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeterListViewSet(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        snippets = Meter.objects.filter(meter_sum=False)
        serializer = MeterSerializer(snippets, context={"request": request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = MeterEditSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MetersBySiteView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, site, format=None):
        snippets = Meter.objects.filter(site_id=int(site), meter_sum=False)
        serializer = MeterSerializer(snippets, context={"request": request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MeterByIdView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        snippet = get_object_or_404(Meter, id=pk)
        serializer = MeterSerializer(snippet)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        snippet = get_object_or_404(Meter, id=pk)
        serializer = MeterEditSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        snippet = get_object_or_404(Meter, id=pk)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MetersByCompanyView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, company, format=None):
        site = self.request.query_params.get('site', None)
        q = Q()
        if site:
            if site.lower() == 'false':
                q &= Q(site__isnull=True)
        snippet = Meter.objects.filter(company_id=int(company), meter_sum=False).filter(q)
        serializer = MeterSerializer(snippet, context={"request": request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class CompanyFilterListViewSet(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        name = self.request.query_params.get('name', None)
        q = Q()
        if name == None or name == '':
            return Response({'companies': 'No data'}, status=status.HTTP_404_NOT_FOUND)
        companies = Company.objects.filter(Q(name__icontains=name) | Q(surname__icontains=name)
                                           | Q(nom_entrepise__icontains=name))
        serializer = CompanySerializer(companies, context={"request": request}, many=True)
        response = Response(serializer.data, status=status.HTTP_200_OK)
        return response


class MeterByNameView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        meter = self.request.query_params.get('meter', None)
        snippet = get_object_or_404(Meter, meter_id=meter)
        serializer = MeterSerializer(snippet)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MeterDeleteByNameView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        meter = self.request.query_params.get('meter', None)
        snippet = get_object_or_404(Meter, meter_id=meter)
        serializer = MeterSerializer(snippet)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, format=None):
        meter = self.request.query_params.get('meter', None)
        snippet = get_object_or_404(Meter, meter_id=meter)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class AnalyticsGeneralView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        dat_from = self.request.query_params.get('date_from', None)
        dat_to = self.request.query_params.get('date_to', None)
        client = self.request.query_params.get('client', None)
        q = Q()
        ql = Q()
        
        if client:
            q &= Q(company_id=int(client))
            ql &= Q(client_id=int(client))


        if dat_from and dat_to:
            date_from = datetime.strptime(dat_from, '%d.%m.%Y')
            date_to = datetime.strptime(dat_to, '%d.%m.%Y') + timedelta(days=1)
            q &= Q(created__gte=date_from, created__lte=date_to)
            ql &= Q(created__gte=date_from, created__lte=date_to)

        offers = Offer.objects.filter(q).filter(lis_force=False)
        offers_signee = offers.filter(offer_status='signee')
        crees = len(offers)
        signee_crees = len(offers_signee)

        logs = ClientLog.objects.filter(ql)

        print 'logs = ', logs

        offers_send = len(logs.filter(log_type='send'))
        email_open = len(logs.filter(log_type='open'))
        email_click = len(logs.filter(log_type='click'))

        desktop = len(logs.filter(device='desktop'))
        mobile = len(logs.filter(device='mobile'))

        print 'offers_send', offers_send

        from django.db.models.functions import ExtractWeekDay

        weekdays = logs.annotate(weekday=ExtractWeekDay('created')).values('weekday').annotate(count=Count('id')).values('weekday', 'count')
        
        print 'weekday= ', weekdays
        try:
            max_weekday = max(weekdays, key=lambda x: x['count'])
        except:
            max_weekday = {
                "count": 0,
                "weekday": 1
            }

        if max_weekday['weekday'] == 1:
            max_weekday['weekday'] = 7
        else:
            max_weekday['weekday'] = max_weekday['weekday']-1
        print max_weekday

        group_client = logs.values('client__name').annotate(count=Count('id')).values('client__name', 'client__surname', 'client__nom_entrepise', 'count')
        group_sorted = sorted(group_client, key=lambda item: item['count'], reverse=True)

        # print logs

        # group_city = logs.values('city').exclude(city__isnull=True).annotate(count=Count('id')).values('country', 'city', 'count')
        group_city = logs.values('city').exclude(city__isnull=True).exclude(city='').exclude(
            city='Mountain View').annotate(count=Count('city')).values('city', 'count')
        
        print(group_city)
        
        group_city = sorted(group_city, key=lambda item: item['count'], reverse=True)

        all_group_city = logs.values('country').exclude(city__isnull=True).exclude(city='').exclude(latitude=None).exclude(longitude=None).annotate(
            count=Count('city')).values('country', 'count', 'latitude', 'longitude')

        return Response(OrderedDict([('len_logs', len(logs)),
                                     ('len_desktop', desktop),
                                     ('len_mobile', mobile),
                                     ('created', crees),
                                     ('offers_send', int(offers_send)),
                                     ('email_open', int(email_open)),
                                     ('email_click', int(email_click)),
                                     ('signee_offers', int(signee_crees)),
                                     ('max_weekday', max_weekday),
                                     ('group_sorted', group_sorted[:3]),
                                     ('all_country', all_group_city),
                                     ('group_city', group_city[:4]),
                                    ]),
                        status=status.HTTP_200_OK)




class ClientLogListView(APIView):
    # authentication_classes = (JSONWebTokenAuthentication, )
    # permission_classes = (IsAuthenticated, )

    def get(self, request, format=None):
        dat_from = self.request.query_params.get('date_from', None)
        dat_to = self.request.query_params.get('date_to', None)
        client = self.request.query_params.get('client', None)
        pag = self.request.query_params.get('pag', None)
        nr = self.request.query_params.get('nr', None)
        user = self.request.query_params.get('user', None)

        name = self.request.query_params.get('name', '')

        if not pag:
            pag = 1
        last = 0
        first = 0
        q = Q()

        if name != '':
            q &= Q(Q(client__name__icontains=str(name)) | Q(client__nom_entrepise__icontains=str(name)))

        if client:
            q &= Q(client_id=int(client))

        if dat_from and dat_to:
            date_from = datetime.strptime(dat_from, '%d.%m.%Y')
            date_to = datetime.strptime(dat_to, '%d.%m.%Y') + timedelta(days=1)
            q &= Q(created__gte=date_from, created__lte=date_to)

        snippets = ClientLog.objects.filter(q).order_by('-created')
        
        if nr:
            per_page = int(nr)
        else:
            per_page = 10
        if int(len(snippets)) % per_page == 0:
            leng = len(snippets)/per_page
        else:
            leng = len(snippets)/per_page + 1
        if pag == leng:
            first = int(len(snippets)/per_page)*per_page
            last = len(snippets)
        else:
            if int(pag) == 1:
                first = 0
                last = per_page
            else:
                last = int(pag) * per_page
                first = last - per_page
        print first, last
        
        try:
            profile = Profile.objects.get(user=User.objects.get(id=int(user)))
            profile.log = snippets[0].created
            profile.save()
            print profile, snippets[0].created
        except:
            print 'No profile'
        
        serializer = ClientLogSerializer(snippets[first:last], context={"request": request}, many=True)

        return Response(OrderedDict([('pages', leng),
                                     ('pag', int(pag)),
                                     ('result', serializer.data)]),
                        status=status.HTTP_200_OK)


class ClientLogTopView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        user = self.request.query_params.get('user', None)

        if user and user != '' and user > 0:
            try:
                last_log = Profile.objects.get(user=User.objects.get(id=int(user))).log
            except:
                return Response(OrderedDict([('nr', 0),
                                             ('logs', [])]),
                                status=status.HTTP_200_OK)
            if last_log:
                logs = ClientLog.objects.filter(created__gt=last_log).order_by('-created')
            else:
                return Response(OrderedDict([('nr', 0),
                                      ('logs', [])]),
                         status=status.HTTP_200_OK)
        else:
            logs = ClientLog.objects.all().order_by('-created')

        serializer = ClientLogSerializer(logs[:5], context={"request": request}, many=True)
        return Response(OrderedDict([('nr', len(logs)),
                                     ('logs', serializer.data)]),
                        status=status.HTTP_200_OK)


class ClientLogByIdView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        dat_from = self.request.query_params.get('date_from', None)
        dat_to = self.request.query_params.get('date_to', None)
        cl = self.request.query_params.get('client', None)
        if cl == '':
            return Response([], status=status.HTTP_400_BAD_REQUEST)

        client = get_object_or_404(Company, id=int(cl))

        q = Q()
        if client:
            q &= Q(client=client)

        if dat_from and dat_to:
            date_from = datetime.strptime(dat_from, '%d.%m.%Y')
            date_to = datetime.strptime(dat_to, '%d.%m.%Y') + timedelta(days=1)
            q &= Q(created__gte=date_from, created__lte=date_to)

        snippets = ClientLog.objects.filter(q).order_by('-created')
       
        serializer = ClientLogSerializer(snippets, context={
                                         "request": request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ClientLastLogListView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        pag = self.request.query_params.get('pag', 1)
        nr = self.request.query_params.get('nr', None)
        name = self.request.query_params.get('name', None)
        if not pag:
            pag = 1
        last = 0
        first = 0
        q = Q()
        if name:
            q &= Q(Q(name__icontains=name) | Q(surname__icontains=name)
                                           | Q(nom_entrepise__icontains=name))
        snippets = Company.objects.filter(q).order_by('-pk')
        if nr:
            per_page = int(nr)
        else:
            per_page = 10
        if int(len(snippets)) % per_page == 0:
            leng = len(snippets)/per_page
        else:
            leng = len(snippets)/per_page + 1
        if pag == leng:
            first = int(len(snippets)/per_page)*per_page
            last = len(snippets)
        else:
            if int(pag) == 1:
                first = 0
                last = per_page
            else:
                last = int(pag) * per_page
                first = last - per_page
        print first, last
        with_data = filter(lambda item: item.last_log !=  None, list(snippets))
        without_data = filter(lambda item: item.last_log == None, list(snippets))
        result = sorted(list(with_data), key=lambda item: item.last_log, reverse=True)
        result = result + without_data
        serializer = CompanyLogDataSerializer(result[first:last], context={"request": request}, many=True)
        return Response(OrderedDict([('pages', leng),
                                     ('pag', int(pag)),
                                     ('result', serializer.data)]),
                        status=status.HTTP_200_OK)


class OfferClientLogLastView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        off = self.request.query_params.get('offer', None)
        cl = self.request.query_params.get('client', None)
        try:
            offer = Offer.objects.get(id=int(off))
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        try:
            client = Company.objects.get(id=int(cl))
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        snippets = ClientLog.objects.filter(offer=offer, client=client, log_type__in=['open', 'click']).order_by('-created')
        per_page = len(snippets)
        
        click_times = ClientLog.objects.filter(offer=offer, client=client, log_type='open').values_list('created', flat=True).order_by('-created')
        refuse_times = ClientLog.objects.filter(offer=offer, client=client, log_type='click').values_list('created', flat=True).order_by('-created')
        
        print refuse_times
        click_times

        times = 0
        if len(click_times) > len(refuse_times):
            times = len(refuse_times)
        else:
            times = len(click_times)

        timp = []
        for ind in range(times):
            if refuse_times[ind] > click_times[ind]:
                timp.append(round((refuse_times[ind] - click_times[ind]).total_seconds()))
            else:
                timp.append(round((click_times[ind] - refuse_times[ind]).total_seconds()))

        try:
            # med_time = sum(timp) / float(len(timp))
            med_time = sum(timp)
        except:
            med_time = 0
        
        try:
            last_snippet = [snippets[0]]
        except:
            last_snippet = []
        serializer = ClientLogSerializer(last_snippet, context={"request": request}, many=True)
        offer_serializer = OfferMetersSerializer(offer)

        return Response(OrderedDict([('per_page', per_page),
                                     ('med_time', abs(med_time)),
                                     ('logs', serializer.data),
                                     ('offer', offer_serializer.data)]),
                        status=status.HTTP_200_OK)


class SMEInsertMailSet(APIView):
    # authentication_classes = (JSONWebTokenAuthentication, )
    # permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        snippets = SmeEmail.objects.all().order_by('-pk')
        serializer = SmeEmailSerializer(snippets, context={"request": request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def post(self, request, format=None):
        try:
            emails = request.data['email']['mailRows']
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        SmeEmail.objects.all().delete()
        for email in emails:
            odata = {
                'email': email['mailname']
            }
            serializer = SmeEmailSerializer(data=odata)
            print 'valid = ', serializer.is_valid()
            if serializer.is_valid():
                serializer.save()

        return Response({'sme emails': emails}, status=status.HTTP_201_CREATED)
