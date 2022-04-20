from django.conf.urls import include, url
from . import views
from .apiviews import *
from .views import *
from django.contrib.auth import views as auth_views


urlpatterns = [

    url(r'create/$', TranslationViewSet.as_view()),
    url(r'truncate/$', DeleteTranslations.as_view()),
    url(r'year/(?P<year>[0-9]+)/company/(?P<company>[0-9]+)/site/(?P<site>[0-9]+)/$', TranslationByCompanyByYearView.as_view()),

    url(r'data/$', TranslationsByOfferView.as_view()),
    
    url(r'csv/$', SomeModelCSVExportView.as_view()),
    url(r'budget/$', BudgetCSVExportView.as_view()),
    url(r'pfc/$', PFCCSVExportView.as_view()),
    
    url(r'market/$', PFCMarketCSVExportView.as_view()),



    ]
