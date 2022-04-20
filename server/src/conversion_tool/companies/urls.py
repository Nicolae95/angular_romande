from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
from . import views
from .views import *
from .apiviews import *

urlpatterns = [

    url(r'list/$', CompanyListViewSet.as_view()),
    url(r'pagination/$', CompanyPaginationListViewSet.as_view()),
    url(r'id/(?P<pk>[0-9]+)/$', CompanyByIdView.as_view()),
   
    url(r'delete-site/(?P<pk>[0-9]+)/$', SiteByIdView.as_view()),
    
    url(r'site/(?P<pk>[0-9]+)/$', SiteByCompanyView.as_view()),
    url(r'site/filter/(?P<pk>[0-9]+)/$', SiteFilterByCompanyView.as_view()),
    url(r'volume/(?P<pk>[0-9]+)/$', SiteVolumeView.as_view()),
    url(r'cc/(?P<pk>[0-9]+)/$', CCVolumeView.as_view()),
    url(r'filter/', CompanyFilterListViewSet.as_view(), name='filter'),

    url(r'meter/company/(?P<company>[0-9]+)/$', MetersByCompanyView.as_view()),
    url(r'meter/pk/(?P<pk>[0-9]+)/$', MeterByIdView.as_view()),
    url(r'meter/name/$', MeterByNameView.as_view()),
    url(r'meter/dlname/$', MeterDeleteByNameView.as_view()),
    url(r'meters/$', MeterListViewSet.as_view()),
    # url(r'meters/site/(?P<site>[0-9]+)/$', MetersBySiteView.as_view()),

    url(r'sites/$', SiteProfilesListViewSet.as_view()),
    url(r'years/(?P<pk>[0-9]+)/$', YearsBySiteListViewSet.as_view()),

    url(r'dashboard/(?P<site>[0-9]+)/$', DashboardBySiteView.as_view()),
    
    url(r'analytics/$', AnalyticsGeneralView.as_view()),
    url(r'client-log/$', ClientLogListView.as_view()),
    url(r'client-log-top/$', ClientLogTopView.as_view()),    
    url(r'client-log/id/$', ClientLogByIdView.as_view()),
    url(r'last-activity/$', ClientLastLogListView.as_view()),
    url(r'offer-activity/$', OfferClientLogLastView.as_view()),

    url(r'sme-emails/$', SMEInsertMailSet.as_view()),


    ]
