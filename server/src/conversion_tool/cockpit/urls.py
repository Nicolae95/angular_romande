from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
# from . import views
from .views import *
from .apiviews import *

urlpatterns = [

    url(r'list/$', CockpitViewSet.as_view()),
    url(r'offer/(?P<pk>[0-9]+)/$', CockpitOfferView.as_view()),
    # url(r'upload/$', TypeFilesUploadView.as_view()),

    # Cockpit
    url(r'cockpit-news/$', CockpitNewsViewSet.as_view()),
    url(r'cockpit-offer-news/(?P<pk>[0-9]+)/$', CockpitNewsOfferByIdView.as_view()),
    url(r'cockpit-news/(?P<pk>[0-9]+)/$', CockpitNewsByIdView.as_view()),
    url(r'cockpit-client/(?P<pk>[0-9]+)/$', CockpitNewsClientEditView.as_view()),

    # News
    url(r'news/cockpit/(?P<pk>[0-9]+)/$', NewsByCockpitView.as_view()),
    url(r'news/(?P<pk>[0-9]+)/$', NewsByIdView.as_view()),
    url(r'list-news/$', NewsListViewSet.as_view()),
    url(r'category-news/$', NewsCategoryViewSet.as_view()),
    url(r'category-name/$', NewsCategoryViewByName.as_view()),

    # Market
    url(r'cockpit-market/(?P<pk>[0-9]+)/$', CockpitMarketByIdView.as_view()),
    url(r'cockpit-market/all/$', CockpitMarketViewSet.as_view()),
    url(r'cockpit-market/cid/(?P<pk>[0-9]+)/$', CockpitMarketByChartViewSet.as_view()),

    # Chart
    url(r'cockpit-charts/$', ChartViewSet.as_view()),
    url(r'cockpit-chart/(?P<pk>[0-9]+)/$', ChartsByCockpitViewSet.as_view()),
    url(r'market-chart/add/(?P<pk>[0-9]+)/$', ChartAddMarkets.as_view()),
    url(r'cockpit-mail/(?P<pk>[0-9]+)/$', SendMailCockpitViewSet.as_view()),

]
