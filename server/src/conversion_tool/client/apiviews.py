# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import *
from django.db.models import Q
from django.template.loader import get_template
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_auth.serializers import UserDetailsSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView
from rest_framework.renderers import JSONRenderer
from rest_framework_jwt.utils import jwt_decode_handler
from datetime import datetime, timedelta
from pytz import country_timezones
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpRequest
from django.core.files import File
from rest_framework import status
from django.contrib.auth.models import User
from operator import itemgetter
from collections import OrderedDict
import collections
from .models import *
from .serializers import *
from companies.models import *
from companies.serializers import *
from offers.models import *
from offers.utils.send_mail import py_mail
from .utils.permision import AdminPermission
from .utils.user import user_permission
import uuid
from django.contrib.gis.geoip2 import GeoIP2
from django.conf import settings
import base64
from rest_auth.models import TokenModel
from rest_auth.utils import jwt_encode
from rest_auth.app_settings import (
    TokenSerializer, UserDetailsSerializer, LoginSerializer, PasswordResetConfirmSerializer, JWTSerializer, create_token
)

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from django.contrib.auth import (
    login as django_login,
    logout as django_logout
)
from django.views.decorators.debug import sensitive_post_parameters
sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters(
        'password', 'old_password', 'new_password1', 'new_password2'
    )
)

class UsersListViewSet(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated, AdminPermission)

    def add_signature(self, files, user, serializer):
        print(user)
        profile = Profile.objects.get(user=user)
        if files == []:
            profile.signature = None
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        for f in files:
            profile.signature.save('signature-{}.png'.format(str(user.id)), File(f), save=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, format=None):
        decoded = jwt_decode_handler(request.META['HTTP_AUTHORIZATION'][4:])
        if int(decoded['role']) != 1:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        pag = self.request.query_params.get('pag', 1)
        name = self.request.query_params.get('name', None)
        nr = self.request.query_params.get('nr', None)
        last = 0
        first = 0
        q = Q()
        print name
        if name:
            snippets = User.objects.filter(Q(first_name__icontains=str(name))
                                            | Q(last_name__icontains=str(name))).order_by('-pk')

        elif name == None or name == '':
            snippets = User.objects.all().order_by('-pk')

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
        # print jwt_decode_handler(request.META['HTTP_AUTHORIZATION'][4:])
        serializer = UserClientSerializer(snippets[first:last], context={"request": request}, many=True)
        return Response(OrderedDict([('pages', leng),
                                     ('pag', int(pag)),
                                     ('result', serializer.data)]),
                        status=status.HTTP_200_OK)


    def post(self, request, format=None):
        print 'admin data = ', request.data, request.FILES.getlist('files')
        try:
            files = request.FILES.getlist('files')
            del request.data['files']
        except:
            files = []
        
        if not request.data['crm_id']:
            request.data['crm_id'] = None
        print 'final admin data = ', request.data
        serializer = UserClientSerializer(data=request.data)
        print serializer.is_valid()
        if serializer.is_valid():
            user = serializer.save()
            self.add_signature(files, user, serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsersByIdView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated, AdminPermission)

    def add_signature(self, files, user, serializer):
        profile = Profile.objects.get(user=user)
        if files == []:
            profile.signature = None
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        CONTENT_TYPES = ['.png']
        for f in files:
            filename, file_extension = os.path.splitext(f.name)
            if file_extension not in CONTENT_TYPES:
                return Response({'Error': 'File bad format'}, status=status.HTTP_400_BAD_REQUEST)
            profile.signature.save('signature-{}.png'.format(str(user.id)), File(f), save=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, pk, format=None):
        decoded = jwt_decode_handler(request.META['HTTP_AUTHORIZATION'][4:])
        if int(decoded['user_id']) != int(pk):
            return Response(status=status.HTTP_403_FORBIDDEN)
        snippet = get_object_or_404(User, id=pk)
        serializer = UserClientSerializer(snippet)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        # print 'admin data = ', request.data
        try:
            files = request.FILES.getlist('files')
            del request.data['files']
        except:
            files = []
        snippet = get_object_or_404(User, id=pk)
        serializer = UserClientSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            if files:
                user = serializer.save()
                self.add_signature(files, user, serializer)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        snippet = get_object_or_404(User, id=pk)
        snippet.delete()
        return Response(status=status.HTTP_200_OK)


class UserVanduerFilterView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)


    def get(self, request, format=None):
        name = self.request.query_params.get('name', None)
        q = Q()
        snippets = []
        firstname = name.split(' ')[0]
        try:
            lastname  = name.split(' ')[1]
            if lastname != '':
                snippets += Profile.objects.filter(role=2).filter(user__first_name__icontains=str(firstname), user__last_name__icontains=str(lastname))
                snippets += Profile.objects.filter(role=2).filter(user__first_name__icontains=str(lastname), user__last_name__icontains=str(firstname))
        except:
            if firstname == '' and len(name.split(' ')) == 1:
                snippets = Profile.objects.filter(role=2)
            elif len(name.split(' ')) == 1:
                snippets = Profile.objects.filter(role=2).filter(Q(user__first_name__icontains=str(firstname)) | Q(user__last_name__icontains=str(firstname)))

        serializer = ClientSerializer(snippets, context={"request": request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class ProfilesListViewSet(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated, AdminPermission)

    def get(self, request, format=None):
        decoded = jwt_decode_handler(request.META['HTTP_AUTHORIZATION'][4:])
        snippets = Profile.objects.all().order_by('-pk')
        serializer = ClientSerializer(snippets, context={"request": request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = ClientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileByIdView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated, AdminPermission)


    def get(self, request, pk, format=None):
        decoded = jwt_decode_handler(request.META['HTTP_AUTHORIZATION'][4:])
        if int(decoded['user_id']) != int(pk):
            return Response(status=status.HTTP_403_FORBIDDEN)
        snippet = get_object_or_404(Profile, id=pk)
        serializer = ClientSerializer(snippet)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        snippet = get_object_or_404(Profile, id=pk)
        serializer = ClientSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        snippet = get_object_or_404(Profile, id=pk)
        snippet.delete()
        return Response(status=status.HTTP_200_OK)


class ProfileByTokenView(APIView):
    # authentication_classes = (JSONWebTokenAuthentication, )
    # permission_classes = (IsAuthenticated,)

    def get(self, request, token, format=None):
        snippet = get_object_or_404(Profile, token=token)
        serializer = ClientSerializer(snippet)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MailAccesedView(APIView):

    def get(self, request, format=None):
        comp = self.request.query_params.get('user', None)
        offer = self.request.query_params.get('offer', None)
        try:
            ip = request.META.get('HTTP_X_REAL_IP')
        except:
            ip = request.META.get('REMOTE_ADDR')
        print 'ip user = ', ip
        g = GeoIP2()
        country = ''
        city = ''
        latitude = 0
        longitude = 0
        if str(ip) != '127.0.0.1':
            try:
                print g.city(ip)
                if g.city(ip)['country_code'] == 'MD':
                    country = 'RO'
                    city = 'Iasi'
                    latitude = 47.1584549
                    longitude = 27.6014418
                else:
                    country = g.city(ip)['country_code']
                    city = g.city(ip)['city']
                    latitude = g.city(ip)['latitude']
                    longitude = g.city(ip)['longitude']
            except:
                country = ''
                city = ''
        # print g.city('109.185.174.82')
        try:
            offer = Offer.objects.get(unique_id=offer)
            client = Company.objects.get(id=int(comp))
            cl = ClientLog(offer=offer, client=client, ip=str(ip),
                           log_type='open', country=country, city=city, latitude=latitude, longitude=longitude)
            cl.save()
        except:
            return Response({"offer was not accesed": "ok"}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"data accesed":"ok"}, status=status.HTTP_200_OK)



class ChangePassMailByIdView(APIView):
    # authentication_classes = (JSONWebTokenAuthentication, )
    # permission_classes = (IsAuthenticated,)

    def generate_email_content(self, obj, profile, url):
        
        try:
            pdf_logo = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media/logo/romande-energie.png')
            with open(pdf_logo, "rb") as lfile:
                encoded_logo = base64.b64encode(lfile.read())
        except:
            encoded_logo = ''
        
        context = {
            "user": obj,
            "profile": profile,
            "encoded_logo": encoded_logo,
            "url": url
        }
        template = get_template('tool/mail/email-pass.html')
        email_content = template.render(context)
        # print email_content
        return email_content


    def get(self, request, pk, format=None):
        temp = self.request.query_params.get('temp', None)
        snippet = get_object_or_404(Profile, temp=temp)
        serializer = ClientPassSerializer(snippet)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def post(self, request, pk, format=None):
        try:
            obj = Profile.objects.get(temp=request.data['temp'])
            obj.temp = None
            import re
            # print request.data['password'], bool(re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{10,}", request.data['password']))
            if bool(re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{10,}", request.data['password'])):
                obj.auth = 3
                obj.last_auth = datetime.now()
                obj.user.set_password(request.data['password'])
                obj.user.save()
                obj.save()
            else:
                Response({"result": "password is not valid"}, status=status.HTTP_200_OK)
        except:
            return Response({'result': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"result": "password changed"}, status=status.HTTP_200_OK)


    def put(self, request, pk, format=None):

        try:
            obj = Profile.objects.get(id=pk)
        except:
            return Response({'result': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)
        
        if request.get_host() == '79.137.34.74':
            url = request.scheme + '://' + 'energysalesdirect.com:9090'
        else:
            url = request.scheme + '://' + request.get_host()

        print 'try sent email data == ', obj.user.email
        obj.temp = uuid.uuid4()
        obj.save()
        email_content = self.generate_email_content(obj.user, obj, url)
        TO = obj.user.email
        # FROM = 'non.commodity.data@gmail.com'
        FROM = getattr(settings, 'MAIL_NAME')
        py_mail('RE: Votre accès sur la Plateforme e-kWh', email_content, [], TO, FROM)
        return Response({'result': 'Email was send'}, status=status.HTTP_200_OK)


class ResetPassMailByUsernameView(APIView):
    # authentication_classes = (JSONWebTokenAuthentication, )
    # permission_classes = (IsAuthenticated,)

    def generate_email_content(self, obj, profile, url):
        context = {
            "user": obj,
            "profile": profile,
            "url": url
        }
        template = get_template('tool/mail/email-pass.html')
        email_content = template.render(context)
        # print email_content
        return email_content

    def put(self, request, username, format=None):
        try:
            obj = Profile.objects.get(user=User.objects.get(username=username))
        except:
            return Response({'result': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)

        if request.get_host() == '79.137.34.74':
            url = request.scheme + '://' + 'energysalesdirect.com:9090'
        else:
            url = request.scheme + '://' + request.get_host()

        # url = request.scheme + '://' + 's1empprd.re-dmz.ch'

        print 'try sent email data == ', obj.user.email
        obj.temp = uuid.uuid4()
        obj.save()
        email_content = self.generate_email_content(obj.user, obj, url)
        TO = obj.user.email
        # FROM = 'non.commodity.data@gmail.com'
        FROM = getattr(settings, 'MAIL_NAME')
        py_mail('RE: Votre accès sur la Plateforme e-kWh', email_content, [], TO, FROM)
        return Response({'result': 'Email was send'}, status=status.HTTP_200_OK)



class ChangePerPageByIdView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)


    def put(self, request, pk, format=None):
        try:
            profile = Profile.objects.get(user=User.objects.get(id=int(pk)))
            profile.per_pag = int(request.data['per_pag'])
            profile.save()
        except:
            return Response({'result': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"page": "changed"}, status=status.HTTP_200_OK)




class LoginView(GenericAPIView):
    
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer
    token_model = TokenModel

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(LoginView, self).dispatch(*args, **kwargs)

    def process_login(self):
        django_login(self.request, self.user)

    def get_response_serializer(self):
        if getattr(settings, 'REST_USE_JWT', False):
            response_serializer = JWTSerializer
        else:
            response_serializer = TokenSerializer
        return response_serializer

    def login(self):
        self.user = self.serializer.validated_data['user']

        if getattr(settings, 'REST_USE_JWT', False):
            self.token = jwt_encode(self.user)
        else:
            self.token = create_token(self.token_model, self.user,
                                      self.serializer)

        if getattr(settings, 'REST_SESSION_LOGIN', True):
            self.process_login()

    def get_response(self):
        serializer_class = self.get_response_serializer()

        if getattr(settings, 'REST_USE_JWT', False):
            data = {
                'user': self.user,
                'token': self.token
            }
            serializer = serializer_class(instance=data,
                                          context={'request': self.request})
        else:
            serializer = serializer_class(instance=self.token,
                                          context={'request': self.request})

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        # print(request.data)
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data,
                                              context={'request': request})
        cet = pytz.timezone('CET')
        if(self.serializer.is_valid()) == False:
            try:
                user_log = User.objects.get(username=request.data['username'])
                # print(user_log)
                profile = Profile.objects.get(user=user_log)
                if not profile.last_auth:
                    profile.last_auth = datetime.now()
                profile.save()
                date_now = cet.localize(datetime.now(), is_dst=None)
                last_auth = make_naive(profile.last_auth, cet)
                cet_last_auth = cet.localize(last_auth, is_dst=None)
                last_auth_to = cet_last_auth + timedelta(minutes=30)
                print('compare data ', date_now, last_auth_to, date_now < last_auth_to)
                if (date_now < last_auth_to):
                    if profile.auth == 0:
                        print('no acces')
                        return Response({'try': profile.auth}, status=status.HTTP_403_FORBIDDEN)
                    else:
                        print(profile, 'bigger than 0')
                        profile.auth = profile.auth - 1
                        profile.last_auth = datetime.now()
                        profile.save()
                        return Response({'try': profile.auth}, status=status.HTTP_403_FORBIDDEN)
                else:
                    if profile.auth == 0:
                        profile.last_auth = datetime.now()
                        profile.save()
                        return Response({'try': profile.auth}, status=status.HTTP_403_FORBIDDEN)
                    profile.auth = profile.auth - 1
                    profile.last_auth = datetime.now()
                    profile.save()
                    return Response({'try': profile.auth}, status=status.HTTP_403_FORBIDDEN)
            except:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            user_log = User.objects.get(username=request.data['username'])
            profile = Profile.objects.get(user=user_log)
            if not profile.last_auth:
                profile.last_auth = datetime.now()
                profile.save()
            date_now = cet.localize(datetime.now(), is_dst=None)
            last_auth = make_naive(profile.last_auth, cet)
            cet_last_auth = cet.localize(last_auth, is_dst=None)
            last_auth_to = cet_last_auth + timedelta(minutes=30)
            print(date_now , last_auth_to)
            if (date_now < last_auth_to):
                if profile.auth == 0:
                    print('you are blocked for 30 minutes')
                    return Response({'try': profile.auth}, status=status.HTTP_403_FORBIDDEN)
                else:
                    profile.auth = 3
                    profile.last_auth = datetime.now()
                    profile.save()
            else:
                profile.auth = 3
                profile.last_auth = datetime.now()
                profile.save()
            self.serializer.is_valid(raise_exception=True)
            self.login()
            return self.get_response()
