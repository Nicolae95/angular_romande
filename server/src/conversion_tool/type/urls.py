from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
# from . import views
from .views import *
from .apiviews import *

urlpatterns = [

    url(r'upload/$', TypeFilesUploadView.as_view()),
    url(r'list/$', TypeViewSet.as_view()),
    url(r'id/(?P<pk>[0-9]+)/$', TypeByIdView.as_view()),


    ]
