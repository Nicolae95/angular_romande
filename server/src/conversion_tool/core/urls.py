from django.conf.urls import include, url
from . import views
from .apiviews import *
from django.contrib.auth import views as auth_views


urlpatterns = [
    # url(r'^$', views.index, name = 'index'),
    url(r'upload/$', FilesUploadView.as_view()),
    url(r'year/(?P<year>[0-9]+)/company/(?P<company>[0-9]+)/site/(?P<site>[0-9]+)/$', CCByCompanyByYearView.as_view()),
    url(r'y/(?P<year>[0-9]+)/c/(?P<company>[0-9]+)/s/(?P<site>[0-9]+)/$', CCWeeklyByCompanyByYearView.as_view()),

    url(r'volumes/(?P<pk>[0-9]+)/$', VolumesViewSet.as_view()),


    # url(r'^country/(?P<id>\d+)/$', views.sheds, name = 'sheds'),
    # url(r'^units/(?P<meter>\w+)/$', views.units, name = 'units'),
    # # url(r'^chart_json/(?P<meter>\w+)/(?P<datetime_from>\w+)/(?P<datetime_to>\w+)/$', views.chart_json, name = 'chart_json'),
    #
    # url(r'^index/$', views.index, name = 'index'),
    # url(r'^upload/$', views.upload_files, name='upload'),
    # url(r'^chart/(?P<meter>\w+)/(?P<datetime_from>\w+)/(?P<datetime_to>\w+)/(?P<shedule>\w+)/(?P<unit>\w+)/$', views.chart, name='chart'),
    # url(r'^chart-weekly/(?P<meter>\w+)/(?P<datetime_from>\w+)/(?P<datetime_to>\w+)/(?P<shedule>\w+)/(?P<unit>\w+)/$', views.chart_weekly, name='chart_weekly'),
    #
    # url(r'^report/upload/$', views.upload_reports, name='upload_report'),
    # url(r'^report/edit/(?P<id>\d+)/$', views.edit_reports, name='edit_report'),
    # url(r'^report/delete/(?P<id>\d+)/$', views.delete_report, name='delete_report'),
    #
    # url(r'^login/$', auth_views.login, {'template_name': 'tool/auth/login.html'}, name='login'),
    # url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    #
    # url(r'^meter/upload/$', views.upload_meter, name='upload_meter'),
    #
    # url(r'^sites/$', views.sites, name='sites'),
    # url(r'^site/add/$', views.add_site, name='add_site'),
    # url(r'^site/edit/(?P<id>\d+)/$', views.edit_site, name='edit_site'),
    # url(r'^site/delete/(?P<id>\d+)/$', views.delete_site, name='delete_site'),
    #
    #
    # url(r'^company/add/$', views.add_company, name='add_company'),
    # url(r'^company/edit/(?P<id>\d+)/$', views.edit_company, name='edit_company'),
    # url(r'^companies/$', views.companies, name='companies'),
    # url(r'^company/delete/(?P<id>\d+)/$', views.delete_company, name='delete_company'),
    #
    # url(r'^schedules/$', views.shedules, name='shedules'),
    # url(r'^schedule/add/$', views.add_shedule, name='add_shedule'),
    # url(r'^schedule/edit/(?P<id>\d+)/$', views.edit_shedule, name='edit_shedule'),
    # url(r'^schedule/delete/(?P<id>\d+)/$', views.delete_schedule, name='delete_schedule'),
    #
    # url(r'^locations/$', views.locations, name='locations'),
    # url(r'^location/add/$', views.add_location, name='add_location'),
    # url(r'^location/edit/(?P<id>\d+)/$', views.edit_location, name='edit_location'),
    #
    # url(r'^holidays/$', views.holidays, name='holidays'),
    # url(r'^holiday/add/$', views.add_holiday, name='add_holiday'),
    # url(r'^holiday/edit/(?P<id>\d+)/$', views.edit_holiday, name='edit_holiday'),
    # url(r'^holiday/delete/(?P<id>\d+)/$', views.delete_holiday, name='delete_holiday'),
    #
    # url(r'^budgets/$', views.budget_reports, name = 'budgets'),
    # url(r'^budget/upload/$', views.upload_reports_budget, name='upload_reports_budget'),
    # url(r'^budget/edit/(?P<id>\d+)/$', views.edit_reports_budget, name='edit_reports_budget'),
    # url(r'^budget/delete/(?P<id>\d+)/$', views.delete_report_budget, name='delete_report_budget'),
    #
    # url(r'^translations/$', views.translations, name = 'translations'),
    # url(r'^translation/upload/$', views.upload_translation, name='upload_translation'),
    # url(r'^translation/edit/(?P<id>\d+)/$', views.edit_translation, name='edit_translation'),
    #
    # url(r'^sum/$', views.meters_sum, name='meters_sum'),
    # url(r'^sum/upload/$', views.upload_meters_sum, name='upload_meters_sum'),
    # url(r'^sum/edit/(?P<id>\d+)/$', views.edit_meters_sum, name='edit_meters_sum'),
    # url(r'^sum/delete/(?P<id>\d+)/$', views.delete_meters_sum, name='delete_meters_sum'),
    #
    # url(r'^files/$', views.files, name='files'),
    # url(r'^file/delete/(?P<id>\d+)/$', views.delete_file, name='delete_file'),

    ]
