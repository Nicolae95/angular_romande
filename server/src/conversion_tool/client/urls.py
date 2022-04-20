from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
from . import views
from .views import *
from .apiviews import *

urlpatterns = [

    url(r'client/list/$', UsersListViewSet.as_view()),
    url(r'client/id/(?P<pk>[0-9]+)/$', UsersByIdView.as_view()),
    url(r'list/$', ProfilesListViewSet.as_view()),
    url(r'id/(?P<pk>[0-9]+)/$', ProfileByIdView.as_view()),

    url(r'mail/$', MailAccesedView.as_view()),

    url(r'client/filter/$', UserVanduerFilterView.as_view()),
    
    url(r'change/pass/(?P<pk>[0-9]+)/$', ChangePassMailByIdView.as_view()),
    url(r'reset/pass/(?P<username>\w+)/$', ResetPassMailByUsernameView.as_view()),
    url(r'page/(?P<pk>[0-9]+)/$', ChangePerPageByIdView.as_view()),

    # url(r'protected/(?P<file_path>\w+)$', views.serve_media, name='serve_media'),


    # url(r'site/(?P<site>[0-9]+)/$', SiteByCompanyView.as_view()),
    #
    # url(r'meter/company/(?P<company>[0-9]+)/$', MetersByCompanyView.as_view()),
    # url(r'meter/pk/(?P<pk>[0-9]+)/$', MeterByIdView.as_view()),
    # url(r'meters/$', MeterListViewSet.as_view()),
    #
    # url(r'sites/$', SiteProfilesListViewSet.as_view()),


    ]
