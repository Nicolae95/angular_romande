from django.contrib import admin
from .models import *


class PfcAdmin(admin.ModelAdmin):
    list_display = (
        'created', 'pfc_id'
    )
    list_filter = (
        'pfc_id', 'created'
    )
    search_fields = ('pfc_id', 'created')


class PfcMarketAdmin(admin.ModelAdmin):
    list_display = (
        'created', 'pfc_id'
    )
    list_filter = (
        'pfc_id', 'created'
    )
    search_fields = ('pfc_id', 'created')


class PfcConsumptionFileAdmin(admin.ModelAdmin):
    list_display = (
        'created', 'data_file', 'pfc'
    )
    list_filter = (
        'pfc', 'created'
    )
    search_fields = ('pfc', 'data_file', 'created')


class PfcConsumptionRecordAdmin(admin.ModelAdmin):
    list_display = (
        'interval_start', 'interval', 'value', 'pfc', 'from_file'
    )
    # list_editable = ('confirmed_status',)
    list_filter = (
        'pfc__pfc_id', 'from_file', 'pfc__created'
    )
    search_fields = ('interval_start', 'from_file')


class PfcMarketConsumptionRecordAdmin(admin.ModelAdmin):
    list_display = (
        'interval_start', 'interval', 'value', 'pfc_market', 'from_file'
    )
    # list_editable = ('confirmed_status',)
    list_filter = (
        'pfc_market__pfc_id', 'from_file', 'pfc_market__created'
    )
    search_fields = ('interval_start', 'pfc_market__created', 'from_file')


admin.site.register(PFC, PfcAdmin)
admin.site.register(PFCMarket, PfcMarketAdmin)
admin.site.register(PfcConsumptionFile, PfcConsumptionFileAdmin)
admin.site.register(PfcMarketConsumptionRecord, PfcMarketConsumptionRecordAdmin)
admin.site.register(PfcConsumptionRecord, PfcConsumptionRecordAdmin)
admin.site.register(PfcPeakRecord)
