from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
from . import views
from .views import *
from .apiviews import *

urlpatterns = [

    # url(r'create/$', views.create_budget, name='create'),
    url(r'list/$', BudgetListViewSet.as_view()),
    url(r'offer/(?P<site>[0-9]+)/$', BudgetByOfferView.as_view()),
    url(r'id/(?P<pk>[0-9]+)/$', BudgetByIdView.as_view()),
    url(r'data/(?P<offer>[0-9]+)/$', BudgetDataByOfferView.as_view()),
    url(r'year/(?P<year>[0-9]+)/company/(?P<company>[0-9]+)/site/(?P<site>[0-9]+)/$', WeeklyByCompanyByYearView.as_view()),

    url(r'history/(?P<offer>[0-9]+)/$', BudgetHistoryDataByOfferView.as_view()),
    
    url(r'lissage/$', OfferBudgetLisForceViewSet.as_view()),


    ]
