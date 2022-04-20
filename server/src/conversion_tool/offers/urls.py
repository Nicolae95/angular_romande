from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
from . import views
from .views import *
from .apiviews import *

urlpatterns = [

    url(r'list-extern/$', OfferExternViewListSet.as_view()),
    url(r'id-extern/(?P<pk>[0-9]+)/$', OfferExternByIdView.as_view()),
    url(r'emp-id/$', OfferAddEMPIdSet.as_view()),

    url(r'lissage/$', OfferLissageView.as_view()),
    url(r'list/$', OffersViewSet.as_view()),
    url(r'id/(?P<pk>[0-9]+)/$', OfferByIdView.as_view()),

    url(r'mail/(?P<pk>[0-9]+)/$', OfferSendMailByIdView.as_view()),
    url(r'mail-function/(?P<pk>[0-9]+)/$', OfferSendFonctionMailByIdView.as_view()),
    url(r'mail-admin/(?P<pk>[0-9A-Fa-f-]+)/$', OfferSendAdminMailByIdView.as_view()),
    url(r'mail-pdf/(?P<pk>[0-9]+)/$', OfferSendPdfMailByIdView.as_view()),
    url(r'mail-thanks/(?P<pk>[0-9]+)/$', OfferSendThanksMailByIdView.as_view()),
    url(r'mail-sme/(?P<pk>[0-9]+)/$', OfferSendSMEMailView.as_view()),

    url(r'cockpit/(?P<pk>[0-9]+)/$', OfferByIdCockpitView.as_view()),
    url(r'status/(?P<pk>[0-9]+)/$', OfferByIdStatusView.as_view()),
    url(r'signed/(?P<pk>[0-9]+)/$', OfferByIdSignedYearsView.as_view()),
    url(r'pfc/(?P<pk>[0-9]+)/$', OfferByIdPfcView.as_view()),
    url(r'emails/$', OfferInsertMailSet.as_view()),
    url(r'energy/$', OfferByPfcEnergyView.as_view()),

    url(r'company/(?P<company>[0-9]+)/$', OfferByCompanyViewSet.as_view()),
    url(r'company-list/(?P<company>[0-9]+)/$', OfferListByCompanyViewSet.as_view()),
    url(r'riscs/$', RiscsViewListSet.as_view()),
    url(r'records/riscs/$', RiscsRecordViewListSet.as_view()),

    url(r'pfcs/(?P<pk>[0-9]+)/$', OfferByIdCockpitYearsView.as_view()),
    url(r'constants/$', ConstantsView.as_view()),
   
    url(r'grds/$', GRDViewListSet.as_view()),
    url(r'grd/(?P<pk>[0-9]+)/$', GRDByIdViewSet.as_view()),

    url(r'upload/signed/$', OfferSigneViewListSet.as_view()),
    url(r'upload/eligibilite/$', OfferEligibiliteViewListSet.as_view()),

    url(r'stop/$', OfferStopViewListSet.as_view()),

    url(r'parameters/(?P<pk>[0-9]+)/$', OfferParametersByIdView.as_view()),

    url(r'pdf-unsigned/$', OfferPdfUnsignedExportView.as_view()),
    url(r'pdf-signed/$', OfferPdfSignedExportView.as_view()),

    ]
