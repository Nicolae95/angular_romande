from django.conf.urls import include, url
from . import views
from django.contrib.auth import views as auth_views
from .views import *
from .apiviews import *

urlpatterns = [

    url(r'upload/$', PfcFilesUploadView.as_view(), name='upload'),

    url(r'upload-api/$', PfcAPIUploadView.as_view(), name='upload_api'),
    url(r'update-api/$', PfcAPIUpdatePermissionView.as_view(), name='update_api'),
    url(r'update-cockpit/$', UpdateCockpitSpecialView.as_view(), name='updatec_api'),

    url(r'files/$', PFCFileViewSet.as_view(), name='files'),
    # url(r'market/$', views.pfc_market_upload_files, name='market_upload'),

    url(r'list/$', PFCViewSet.as_view(), name='pcfs'),
    # url(r'market/list/$', PFCMarketViewSet.as_view(), name='market_pcfs'),

    url(r'year/(?P<year>[0-9]+)/$', PfcRecordsByYearView.as_view()),
    # url(r'market-year/(?P<year>[0-9]+)/$', PfcMarketRecordsByYearView.as_view()),

    url(r'detail/(?P<pk>[0-9]+)/$', PFCByIdView.as_view()),
    url(r'date/$', PFCByDateView.as_view()),
    url(r'detail-market/(?P<pk>[0-9]+)/$', PFCMarketByIdView.as_view()),

    url(r'units/$', PfcRecordsUnitsView.as_view(), name='pcfs_units'),
    url(r'riscs/$', PfcRiscsByYearView.as_view(), name='pcfs_riscs'),
    url(r'peak/$', PFCPeakDataView.as_view(), name='pcfs_peak'),
    
    url(r'opportunites/$', PfcSmeOportunitiesTodayView.as_view(), name='pcfs_riscs'),
    url(r'upload-sme/$', PfcSmeCockpitView.as_view(), name='uploadd_api'),

    url(r'years/$', PfcFirstRecordView.as_view()),


    # url(r'truncate/$', DeletePFCS.as_view(), name='pcfs_delete'),

    ]
