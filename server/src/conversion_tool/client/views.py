from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
import json
import pytz
import os
from os.path import basename
import StringIO
from .serializers import *
from .models import *
from companies.models import *
from cockpit.models import *
from core.models import *
from offers.models import *
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework_jwt.utils import jwt_decode_handler
from rest_framework import status
from django.core.files import File
from django.conf import settings
import base64

# Create your views here.


class SignatureView(View):

    def get(self, request, *args, **kwargs):
        fid = request.GET['file']
        try:
            profile = Profile.objects.get(id=int(fid))
            pdf = offer.unsigned_file
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="{}"'.format(str(pdf))
        except:
            return response
        return response


def eligibilite_media(request, id):
    """
    location /protected/ {
        add_header Access-Control-Allow-Origin *;
        internal;
        alias /root/romande/server/src/conversion_tool/media/;
    }
    """
    token = request.META.get('HTTP_AUTHORIZATION')[4:]
    pdf = Offer.objects.get(id=int(id)).eligibilite
    response = HttpResponse()
    response['Content-Type'] = ''
    print '/protected/' + pdf.name
    try:
        decoded = jwt_decode_handler(token)
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(
            pdf.name.encode('utf8'))
        response['X-Accel-Redirect'] = '/protected/' + pdf.name.encode('utf8')
        return response
    except:
        return response


def unsigned_media(request, id):
    token = request.META.get('HTTP_AUTHORIZATION')[4:]
    pdf = Offer.objects.get(id=int(id)).unsigned_file
    # print('file name ', pdf.name)
    response = HttpResponse()
    response['Content-Type'] = ''
    # print '/protected/' + pdf.name
    print(os.path.basename(pdf.name))
    try:
        decoded = jwt_decode_handler(token)
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(
            pdf.name.encode('utf8'))
        response['X-Accel-Redirect'] = '/protected/' + pdf.name.encode('utf8')
        return response
    except:
        return response


def signed_media(request, id):
    token = request.META.get('HTTP_AUTHORIZATION')[4:]
    pdf = Offer.objects.get(id=int(id)).signed_file
    response = HttpResponse()
    response['Content-Type'] = ''
    try:
        decoded = jwt_decode_handler(token)
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(
            pdf.name.encode('utf8'))
        response['X-Accel-Redirect'] = '/protected/' + pdf.name.encode('utf8')
        return response
    except:
        return response


def protected_signature(request, id):
    try:
        token = request.META.get('HTTP_AUTHORIZATION')[4:]
        decoded = jwt_decode_handler(token)
        image = Profile.objects.get(id=int(id)).signature
        sign = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                            'media/{}'.format(str(image)))
        with open(sign, "rb") as sfile:
            encoded_signature = base64.b64encode(sfile.read())
        # response['Content-Type'] = ''
        # response['X-Accel-Redirect'] = '/protected/' + image.name.encode('utf8')
        response = HttpResponse(json.dumps(
            {'image': encoded_signature}), content_type="application/json")
        return response
    except:
        return HttpResponse(status=404)


def protected_demo(request, file_path):
    token = request.META.get('HTTP_AUTHORIZATION')[4:]
    # response = HttpResponse()
    # response['Content-Type'] = ''
    if file_path == 'Multi_PODs' or file_path == 'PFC' or file_path == 'Un_POD' or file_path == 'volume':
        try:
            decoded = jwt_decode_handler(token)
            file_path = os.path.join(os.path.dirname(os.path.dirname(
                __file__)), 'media' + os.sep + 'demo' + os.sep + file_path + '.xlsx')
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
        except:
            return HttpResponse(status=404)
    else:
        return HttpResponse(status=404)


def protected_site(request, id):
    # token = request.GET.get('q', '')
    token = request.META.get('HTTP_AUTHORIZATION')[4:]
    site = Site.objects.get(id=int(id))
    file = EnergyConsumptionFile.objects.get(site=site).data_file
    # print file.name
    CONTENT_TYPES = ['.xlsx', '.xls']
    filename, file_extension = os.path.splitext(file.name)
    if file_extension in CONTENT_TYPES:
        try:
            decoded = jwt_decode_handler(token)
            file_path = os.path.join(os.path.dirname(
                os.path.dirname(__file__)), 'media' + os.sep + file.name)
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            # response['X-Accel-Redirect'] = '/protected/' + file.name.encode('utf8')
            return response
        except:
            return HttpResponse(status=404)
    else:
        return HttpResponse(status=404)


def unsigned_pdf(request, id):
    file = request.GET.get('file', '')
    token = request.META.get('HTTP_AUTHORIZATION')[4:]
    # pdf = Offer.objects.get(id=int(id)).unsigned_file
    print file, file.encode('utf8')
    # file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media' + os.sep + 'unsigned' + os.sep + file.encode('utf8'))
    # print file_path
    response = HttpResponse()
    response['Content-Type'] = ''
    # print '/protected/' + pdf.name
    try:
        decoded = jwt_decode_handler(token)
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(file.encode('utf8'))
        response['X-Accel-Redirect'] = '/protected/' + 'unsigned' + os.sep + file.encode('utf8')
        return response
    except:
        return response


def cockpit_chart(request, id):
    try:
        image = Chart.objects.get(id=int(id)).image
        print image, image.name.encode('utf8')
        sign = os.path.join(os.path.dirname(os.path.dirname(__file__)),'media/{}'.format(str(image)))
        response = HttpResponse()
        response['Content-Type'] = ''
        response['X-Accel-Redirect'] = '/protected/' + image.name.encode('utf8')
        return response
    except:
        return HttpResponse(status=404)
