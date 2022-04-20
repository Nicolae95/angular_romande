from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
# from . import views
from .views import *
from .apiviews import *

urlpatterns = [

    url(r'upload/$', TypePondereFilesUploadView.as_view()),
    url(r'year/(?P<year>[0-9]+)/id/(?P<pondere>[0-9]+)/$', PondereRecordsYearView.as_view()),
    url(r'list/$', PondereViewSet.as_view()),
    # url(r'id/(?P<pk>[0-9]+)/$', TypePondereByIdView.as_view()),


    ]
