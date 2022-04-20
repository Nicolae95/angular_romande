from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sites.models import Site
from django.contrib.auth import views as auth_views
# from rest_framework.authtoken import views as tok_views
admin.site.unregister(Site)
from rest_framework import routers
from core.views import *
from core.apiviews import *
from rest_framework_jwt.views import refresh_jwt_token
from rest_framework_jwt.views import ObtainJSONWebToken
from pfc.apiviews import *
from client.apiviews import *
from companies.apiviews import *
from rest_auth.views import UserDetailsView
from client.views import unsigned_media, unsigned_pdf, signed_media, protected_signature, eligibilite_media, protected_demo, protected_site, cockpit_chart

# django rest framework router
router = routers.DefaultRouter()
# end of django rest framework router


urlpatterns = [
    # url(r'^api/', include(router.urls)),
    # url(r'^api/reports/$', ReportsViewSet.as_view()),
    # url(r'^api/reports/(?P<pk>[0-9]+)/$', ReportViewSet.as_view()),
    # url(r'^api/reports/company/(?P<company>\w+)/$', ReportsCompanyViewSet.as_view()),
    # url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # url(r'api-token-auth/', tok_views.obtain_auth_token),
    # url(r'^api/upload/$', FilesUploadView.as_view()),
    # url(r'^api-email/', ObtainJSONWebToken.as_view(serializer_class=CustomJWTSerializer)),

    url(r'^api/', include(router.urls)),
    # url(r'^api/auth/', include('rest_auth.urls')),
    url(r'^api/auth/user/', UserDetailsView.as_view()),
    url(r'^api/auth/login/', LoginView.as_view()),
    
    url(r'^api/token/', refresh_jwt_token),
    url(r'^api-auth/registration/', include('rest_auth.registration.urls')),

    url(r'^api/pfc-market/year/(?P<year>[0-9]+)/$', PfcMarketRecordsByYearView.as_view()),
    url(r'^api/pfc-market/list/$', PFCMarketViewSet.as_view()),
    url(r'^api/pods/site/(?P<site>[0-9]+)/$', MetersBySiteView.as_view()),

    url(r'^api/user', include('client.urls', namespace='user')),
    url(r'^api/cc', include('core.urls', namespace='tool')),
    url(r'^api/pfc', include('pfc.urls', namespace='pfc')),
    url(r'^api/budget', include('budget.urls', namespace='budget')),
    url(r'^api/company', include('companies.urls', namespace='company')),
    url(r'^api/offer', include('offers.urls', namespace='offers')),
    url(r'^api/type', include('type.urls', namespace='type')),
    url(r'^api/pondere', include('typepondere.urls', namespace='ptype')),
    url(r'^api/translation', include('translations.urls', namespace='translation')),
    url(r'^api/cockpit', include('cockpit.urls', namespace='cockpit')),
    url(r'^api/datahub', include('datahub.urls', namespace='datahub')),

    url(r'^api/eligibilite/(?P<id>[0-9]+)/$', eligibilite_media, name='eligibilite_media'),
    url(r'^api/unsigned/(?P<id>[0-9]+)/$', unsigned_media, name='unsigned_media'),
    url(r'^api/pdf/(?P<id>[0-9]+)/$', unsigned_pdf, name='unsigned_pdf'),
    url(r'^api/signed/(?P<id>[0-9]+)/$', signed_media, name='signed_media'),
    url(r'^api/signature/(?P<id>[0-9]+)/$', protected_signature, name="protect_media"),
    url(r'^api/sfile/(?P<id>[0-9]+)/$', protected_site, name="protected_site"),
    url(r'^api/demo/(?P<file_path>\w+)/$', protected_demo, name="protect_media"),
    
    url(r'^api/chart/(?P<id>[0-9]+)/$', cockpit_chart, name="cockpit_chart"),

    
    url(r'^admin/', include(admin.site.urls)),
    # url(r'^channels-api/gi', include('channels_api.urls'))

    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
