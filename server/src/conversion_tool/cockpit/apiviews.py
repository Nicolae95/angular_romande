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
from pfc.models import *
from offers.models import *
from .serializers import *
from django.conf import settings
from companies.models import Company
from offers.utils.send_mail import py_mail
from utils.mail import generate_cockpit_mail



class CockpitNewsByIdView(APIView):
    # authentication_classes = (JSONWebTokenAuthentication, )
    # permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        snippet = get_object_or_404(CockpitNews, id=pk)
        serializer = CockpitNewsDataSerializer(snippet)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, pk, format=None):
        snippet = get_object_or_404(CockpitNews, id=pk)
        serializer = CockpitNewsEditSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        snippet = get_object_or_404(CockpitNews, id=pk)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CockpitNewsClientEditView(APIView):
    # authentication_classes = (JSONWebTokenAuthentication, )
    # permission_classes = (IsAuthenticated,)

    def put(self, request, pk, format=None):
        snippet = get_object_or_404(CockpitNews, id=pk)
        serializer = CockpitNewsSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CockpitNewsViewSet(APIView):
    # authentication_classes = (JSONWebTokenAuthentication, )
    # permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        snippets = CockpitNews.objects.all().order_by('-pk')
        serializer = CockpitNewsDataSerializer(snippets, context={"request": request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = CockpitNewsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CockpitNewsOfferByIdView(APIView):
    # authentication_classes = (JSONWebTokenAuthentication, )
    # permission_classes = (IsAuthenticated,)

    def put(self, request, pk, format=None):
        snippet = get_object_or_404(CockpitNews, id=pk)
        serializer = CockpitOfferNewsSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NewsCategoryViewSet(APIView):
    # authentication_classes = (JSONWebTokenAuthentication, )
    # permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        snippets = NewsCategory.objects.all().order_by('-pk')
        serializer = NewsCategorySerializer(snippets, context={"request": request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = NewsCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NewsCategoryViewByName(APIView):
    # authentication_classes = (JSONWebTokenAuthentication, )
    # permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        name = self.request.query_params.get('name', '')
        snippet = get_object_or_404(NewsCategory, name=name)
        serializer = NewsCategorySerializer(snippet)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NewsByIdView(APIView):
    # authentication_classes = (JSONWebTokenAuthentication, )
    # permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        snippet = get_object_or_404(News, id=pk)
        serializer = NewsSerializer(snippet)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, pk, format=None):
        snippet = get_object_or_404(News, id=pk)
        serializer = NewsSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        snippet = get_object_or_404(News, id=pk)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class NewsByCockpitView(APIView):
    # authentication_classes = (JSONWebTokenAuthentication, )
    # permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        snippets = News.objects.filter(cockpit=pk).order_by('-pk')
        serializer = NewsSerializer(snippets, context={"request": request}, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class NewsListViewSet(APIView):
    # authentication_classes = (JSONWebTokenAuthentication, )
    # permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        snippets = News.objects.all().order_by('-pk')
        serializer = NewsSerializer(snippets, context={"request": request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = NewsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CockpitMarketViewSet(APIView):
    # authentication_classes = (JSONWebTokenAuthentication, )
    # permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        snippets = CockpitMarket.objects.all().order_by('-pk')
        serializer = CockpitMarketSerializer(snippets, context={"request": request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        try:
            snippet = CockpitMarket.objects.get(market_id=request.data['market_id'])
            serializer = CockpitMarketSerializer(snippet)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except:
            pass

        serializer = CockpitMarketSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CockpitMarketByIdView(APIView):
    # authentication_classes = (JSONWebTokenAuthentication, )
    # permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        snippet = get_object_or_404(CockpitMarket, id=pk)
        serializer = CockpitMarketSerializer(snippet)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, pk, format=None):
        snippet = get_object_or_404(CockpitMarket, id=pk)
        serializer = CockpitMarketSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        snippet = get_object_or_404(CockpitMarket, id=pk)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChartViewSet(APIView):
    # authentication_classes = (JSONWebTokenAuthentication, )
    # permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        snippets = Chart.objects.all().order_by('-pk')
        serializer = ChartMarketSerializer(snippets, context={"request": request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = ChartCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChartAddMarkets(APIView):
    # authentication_classes = (JSONWebTokenAuthentication, )
    # permission_classes = (IsAuthenticated,)

    def put(self, request, pk, format=None):
        snippet = get_object_or_404(Chart, id=pk)
        serializer = ChartAddMarketSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CockpitMarketByChartViewSet(APIView):
    # authentication_classes = (JSONWebTokenAuthentication, )
    # permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        snippets = ChartMarket.objects.filter(id=pk).order_by('-pk')
        serializer = ChartMarketSerializer(snippets, context={"request": request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        snippet = get_object_or_404(Chart, id=pk)
        serializer = ChartEditMarketSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChartsByCockpitViewSet(APIView):
    # authentication_classes = (JSONWebTokenAuthentication, )
    # permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        snippets = Chart.objects.filter(cockpit=pk).order_by('-pk')
        serializer = ChartMarketSerializer(snippets, context={"request": request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SendMailCockpitViewSet(APIView):
    # authentication_classes = (JSONWebTokenAuthentication, )
    # permission_classes = (IsAuthenticated,)

    def put(self, request, pk, format=None):
        if request.get_host() == '79.137.34.74':
            url = request.scheme + '://' + '79.137.34.74:9090'
        elif request.get_host() == 'energysalesdirect.com':
            url = request.scheme + '://' + 'energysalesdirect.com:9090'
        else:
            url = request.scheme + '://' + request.get_host()
        print pk
        cockpit = CockpitNews.objects.get(id=int(pk))
        snippets = Chart.objects.filter(cockpit=pk).order_by('-pk')
        email_content = generate_cockpit_mail(cockpit, snippets, url)
        # print('email content == ', email_content)

        clients = cockpit.clients.all()
        for client in clients:
            TO = Company.objects.get(id=client.id).email
            FROM = getattr(settings, 'MAIL_NAME')
            if cockpit.email_name:
                py_mail(cockpit.email_name, email_content, [], TO, FROM)
            else:
                py_mail(cockpit.name, email_content, [], TO, FROM)
        return Response(status=status.HTTP_200_OK)


class CockpitViewSet(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        cockpits = Cockpit.objects.all()
        data = []
        for cockpit in cockpits:
            if cockpit.id == 1:
                data.append({'id': cockpit.id, 'name': cockpit.name})
            elif cockpit.id == 3:
                data.append({'id': cockpit.id+6, 'name': cockpit.name})
            else:
                for weekday in Weekday.objects.all():
                    data.append({'id': weekday.day+1, 'name': weekday.name})
        return Response(sorted(data), status=status.HTTP_200_OK)


class CockpitOfferView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        try:
            snippets = CockpitOffer.objects.filter(offer_id=pk).order_by('-pk')[0]
            print snippets
        except:
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = CockpitOfferSerializer(snippets)
        return Response(serializer.data, status=status.HTTP_200_OK)


#
# class TypeByIdView(APIView):
#     # def get_object(self, pk):
#     #     try:
#     #         return ProfileType.objects.get(id=int(pk))
#     #     except ProfileType.DoesNotExist:
#     #         return Response(status=status.HTTP_400_BAD_REQUEST)
#
#     def get(self, request, pk, format=None):
#         snippet = get_object_or_404(ProfileType, id=pk)
#         serializer = ProfileTypeSerializer(snippet)
#         return Response(serializer.data)
#
#     def put(self, request, pk, format=None):
#         snippet = get_object_or_404(ProfileType, id=pk)
#         serializer = ProfileTypeSerializer(snippet, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def delete(self, request, pk, format=None):
#         snippet = get_object_or_404(ProfileType, id=pk)
#         snippet.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# class CockpitAPIUpdateView(APIView):
    # authentication_classes = (JSONWebTokenAuthentication, )
    # permission_classes = (IsAuthenticated,)

    # def post(self, request, format=None):

    #     risc = Risc.objects.get(name='Risque PwB')
    #     risc1 = Risc.objects.get(name__icontains='Risque volume')
    #     risc2 = Risc.objects.get(name='Risque prix')

    #     energy1, created3 = Risc.objects.get_or_create(code='energy1')
    #     energy2, created4 = Risc.objects.get_or_create(code='energy2')
    #     energy3, created5 = Risc.objects.get_or_create(code='energy3')
    #     energy4, created6 = Risc.objects.get_or_create(code='energy4')
    #     energy5, created7 = Risc.objects.get_or_create(code='energy5')
    #     energy6, created8 = Risc.objects.get_or_create(code='energy6')

    #     # if PFC.objects.filter(pfc_id=request.data['obj'], time=' ' + request.data['hour']).exists():
    #     #     return Response({'received data': 'such pfc exists'}, status=status.HTTP_400_BAD_REQUEST)

    #     currentPfc = PFC.objects.filter(pfc_id=request.data['obj'])
    #     if currentPfc:
    #         if ' ' + request.data['hour'] != str(currentPfc[0].time):
    #             currentPfc[0].pfc_id = currentPfc[0].pfc_id + ' ' + str(currentPfc[0].time)
    #             currentPfc[0].time = None
    #             currentPfc[0].save()
    #     print 'currentPfc === ', currentPfc

    #     pfc, created = PFC.objects.get_or_create(pfc_id=request.data['obj'], time=' ' + request.data['hour'])
    #     if created:
    #         streampfc = StringIO.StringIO()
    #         writerpfc = csv.writer(streampfc, delimiter='\t')
    #         for index, obj in enumerate(request.data['pfc']):
    #             if index > 0:
    #                 date = datetime.strptime(str(obj[0]), '%d.%m.%Y %H:%M')
    #                 # print([datetime.now(), datetime.now(), pfc.id, float(obj[2]), date, timedelta(hours=1), 'CHF'])
    #                 writerpfc.writerow([datetime.now(), datetime.now(), pfc.id,
    #                                     float(obj[2]), date, timedelta(hours=1), 'CHF'])
    #         upload_pfc_nofile_db(streampfc)

    #         for index, risq in enumerate(request.data['risqs']):
    #             if index > 0:
    #                 # print risq
    #                 RiscRecord.objects.create(risc=risc, value=float(risq[1]), pfc=pfc, year=int(risq[0]))
    #                 RiscRecord.objects.create(risc=risc1, value=float(risq[2]), pfc=pfc, year=int(risq[0]))
    #                 RiscRecord.objects.create(risc=risc2, value=float(risq[3]), pfc=pfc, year=int(risq[0]))

    #         for index, ecoq in enumerate(request.data['eco']):
    #             if index > 0:
    #                 # print ecoq
    #                 RiscRecord.objects.create(risc=energy2, value=float(ecoq[1]), pfc=pfc, year=int(ecoq[0]))
    #                 RiscRecord.objects.create(risc=energy1, value=float(ecoq[2]), pfc=pfc, year=int(ecoq[0]))
    #                 RiscRecord.objects.create(risc=energy6, value=float(ecoq[3]), pfc=pfc, year=int(ecoq[0]))
    #                 RiscRecord.objects.create(risc=energy3, value=float(ecoq[4]), pfc=pfc, year=int(ecoq[0]))
    #                 RiscRecord.objects.create(risc=energy5, value=float(ecoq[5]), pfc=pfc, year=int(ecoq[0]))
    #                 RiscRecord.objects.create(risc=energy4, value=float(ecoq[6]), pfc=pfc, year=int(ecoq[0]))

    #     today = datetime.now().date()
    #     day = today.day()
    #     offers = CockpitOffer.objects.filter(cockpit_id=2, weekday__day=day).values_list('offer', flat=True)

    #     print 'offers ===== ', offers
    #     if offers:
    #         for offer in offers:
    #             odata = {
    #                 'id': offer.id,
    #                 'pfc': pfc.id
    #             }
    #             offer.expiration_date = expiration_date(offer.validation_time)
    #             serializer = OfferPfcEditSerializer(offer, data=odata)
    #             # print 'valid = ', offer, serializer.is_valid()
    #             if serializer.is_valid():
    #                 serializer.save()

        # return Response({'received data': len(request.data)}, status=status.HTTP_201_CREATED)
