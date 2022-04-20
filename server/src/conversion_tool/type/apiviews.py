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
import os
from os.path import basename
from xlrd import open_workbook, xldate
from rest_framework import viewsets
from collections import defaultdict
from operator import itemgetter
from rest_framework import status
from .models import *
from .serializers import *


class TypeViewSet(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        snippets = ProfileType.objects.all()
        serializer = ProfileTypeSerializer(snippets, context={"request": request}, many=True)
        return Response(serializer.data)


class TypeByIdView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)
    # def get_object(self, pk):
    #     try:
    #         return ProfileType.objects.get(id=int(pk))
    #     except ProfileType.DoesNotExist:
    #         return Response(status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk, format=None):
        snippet = get_object_or_404(ProfileType, id=pk)
        serializer = ProfileTypeSerializer(snippet)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        snippet = get_object_or_404(ProfileType, id=pk)
        serializer = ProfileTypeSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        snippet = get_object_or_404(ProfileType, id=pk)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TypeFilesUploadView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)
    parser_classes = (FormParser, MultiPartParser)

    def post(self, request, format=None):
        print request.data
        for f in request.FILES.getlist('files'):
            instance = ProfileType(data_file = f, name = request.data['name'], year = int(request.data['year']))
            instance.save()
        return Response({'received data': len(request.data)})


class ConvertUploadView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        from django.core.files.storage import FileSystemStorage
        from logic.calculator.sum import Parsing, ParsingMultisite
        # print request.FILES['files']
        files = []
        fs = FileSystemStorage(location='media/calculator/')
        for file in request.FILES.getlist('files'):
            filename = fs.save(file.name, file)
            outputFilename = os.path.join(os.path.dirname(os.path.dirname(
                __file__)), 'media' + os.sep + 'calculator' + os.sep + filename)
            files.append((outputFilename).encode('utf8'))
        
        result = []
        if request.data['multisite'] == False:
            parsing = Parsing(files, 'site')
            files = parsing.converted_data()
            for file in files:
                result.append(os.path.basename(file['file']))
        else:
            print('multisite')
            parsing = ParsingMultisite(files[0])
            file = parsing.converted_data()
            result.append(os.path.basename(file))
        return Response({'files': result})


class SumUploadView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)


    def post(self, request, format=None):
        from django.core.files.storage import FileSystemStorage
        from logic.calculator.sum import Parsing, ParsingMultisite
        # print request.FILES['files']
        files = []
        fs = FileSystemStorage(location='media/calculator/')
        for file in request.FILES.getlist('files'):
            filename = fs.save(file.name, file)
            outputFilename = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media' + os.sep + 'calculator' + os.sep + filename)
            files.append((outputFilename).encode('utf8'))
        
        if request.data['multisite'] == False:
            parsing = Parsing(files, 'site')
            sum_file = parsing.calculate_sum_site()
            # file_name = os.path.basename(filed)
        else:
            print('multisite')
            parsing = ParsingMultisite(files[0])
            sum_file = parsing.calculate_sum()

        return Response({'file': sum_file})


class DiffUploadView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        from django.core.files.storage import FileSystemStorage
        from logic.calculator.sum import Parsing, ParsingMultisite
        # print request.FILES['files']
        files = []
        fs = FileSystemStorage(location='media/calculator/')
        for file in request.FILES.getlist('files'):
            filename = fs.save(file.name, file)
            outputFilename = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media' + os.sep + 'calculator' + os.sep + filename)
            files.append((outputFilename).encode('utf8'))
        dfile = request.FILES.getlist('diff')[0]
        filename = fs.save(dfile.name, dfile)
        outputFilename = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media' + os.sep + 'calculator' + os.sep + filename)
        diff = outputFilename.encode('utf8')
        parsing = Parsing(files, 'site', diff)
        filed =  parsing.calculate_diff_site()
        file_name = os.path.basename(filed)
        return Response({'file': file_name})


class TranslationUploadView(APIView):
    # authentication_classes = (JSONWebTokenAuthentication, )
    # permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        from django.core.files.storage import FileSystemStorage
        from logic.calculator.sum import Parsing, ParsingMultisite
        # print request.FILES['files']
        files = []
        fs = FileSystemStorage(location='media/calculator/')
        for file in request.FILES.getlist('files'):
            filename = fs.save(file.name, file)
            outputFilename = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media' + os.sep + 'calculator' + os.sep + filename)
            files.append((outputFilename).encode('utf8'))
        try:
            year = int(request.data['year'])
            years_value = request.data['years_value']
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        parsing = Parsing(files, 'translate')
        filed = parsing.translate_site(year, years_value)
        file_name = os.path.basename(filed)
        
        return Response({'file': file_name})
