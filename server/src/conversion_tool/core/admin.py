from django.contrib import admin
from core.models import (
    EnergyConsumptionFile, EnergyConsumptionRecord,
    EnergyConsumptionPeriod, EnergyConsumptionReport,
    DayPattern, Hour, BulkUpload, Shedule, Months, Weekday,
    MonthRecord, SeasonRecord, WeeklyRecord, HeadgeRecord
)


class DayPatternInline(admin.TabularInline):
    model = EnergyConsumptionPeriod.weekdays.through


class EnergyConsumptionPeriodAdmin(admin.ModelAdmin):
    # inlines = [
    #     DayPatternInline,
    # ]
    pass


class EnergyConsumptionFileInline(admin.TabularInline):
    model = EnergyConsumptionFile


class BulkUploadAdmin(admin.ModelAdmin):
    inlines = [
        EnergyConsumptionFileInline,
    ]


class EnergyConsumptionFileAdmin(admin.ModelAdmin):
    list_display = (
        'created', 'data_file', 'site'
    )
    # list_editable = ('confirmed_status',)
    list_filter = (
        'site__name', 'site__company__name', 'created', 'bulk_upload'
    )
    search_fields = ('site__name', 'site__company__name', 'data_file', 'created')

    def get_queryset(self, request):
        queryset = super(self.__class__, self).get_queryset(request)
        return queryset.select_related('site', 'site__company', 'bulk_upload')


class EnergyConsumptionRecordAdmin(admin.ModelAdmin):
    list_display = (
        'interval_start', 'interval', 'value', 'meter', 'from_file'
    )
    # list_editable = ('confirmed_status',)
    list_filter = (
        'meter__meter_id', 'meter__site__name', 'meter__site__company__name',
        'from_file', 'from_file__bulk_upload',  'created'
    )
    search_fields = ('interval_start', 'meter__meter_id', 'meter__site__name', 'meter__site__company__name')

    def get_queryset(self, request):
        queryset = super(self.__class__, self).get_queryset(request)
        return queryset.select_related('meter__site', 'meter__site__company', 'from_file', 'from_file__bulk_upload')


class MonthRecordAdmin(admin.ModelAdmin):
    list_display = (
        'month', 'schedule', 'value', 'meter'
    )
    # list_editable = ('confirmed_status',)
    list_filter = (
        'meter__meter_id', 'meter__site__name', 'meter__site__company__name'
    )
    search_fields = ('month', 'meter__meter_id', 'meter__site__name')


class EnergyConsumptionReportAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'result_file', 'datetime_from', 'datetime_to', 'meter'
    )
    # list_editable = ('confirmed_status',)
    list_filter = (
        'meter__meter_id', 'meter__site__name', 'meter__site__company__name',
        'created'
    )
    search_fields = ('title', 'meter__meter_id', 'meter__site__name', 'meter__site__company__name')

    def get_queryset(self, request):
        queryset = super(self.__class__, self).get_queryset(request)
        return queryset.select_related('meter__site', 'meter__site__company')

# Register your models here.
admin.site.register(EnergyConsumptionFile, EnergyConsumptionFileAdmin)
admin.site.register(EnergyConsumptionRecord, EnergyConsumptionRecordAdmin)
# admin.site.register(EnergyConsumptionPeriod, EnergyConsumptionPeriodAdmin)
admin.site.register(EnergyConsumptionReport, EnergyConsumptionReportAdmin)
admin.site.register(Hour)
# admin.site.register(DayPattern)
admin.site.register(Shedule)
admin.site.register(Months)
admin.site.register(Weekday)

admin.site.register(MonthRecord, MonthRecordAdmin)
admin.site.register(SeasonRecord)
admin.site.register(WeeklyRecord)
admin.site.register(HeadgeRecord)
