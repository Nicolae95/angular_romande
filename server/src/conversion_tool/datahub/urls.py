from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
# from . import views
from .apiviews import *

urlpatterns = [

    url(r'units/$', DatahubUnitsViewSet.as_view()),
    url(r'market/$', DatahubMarketViewSet.as_view()),

    url(r'chart/$', ChartMarketViewSet.as_view()),
    url(r'tabel/$', TabelMarketViewSet.as_view()),


    ]
