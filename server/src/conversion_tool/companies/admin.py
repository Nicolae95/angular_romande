from django.contrib import admin
from core.models import EnergyConsumptionReport
from companies.models import Company, Site, Meter, ClientLog, SmeEmail


class SiteInline(admin.TabularInline):
    model = Site


class CompanyAdmin(admin.ModelAdmin):
    inlines = [
        SiteInline,
    ]


class MeterInline(admin.TabularInline):
    model = Meter


class SiteAdmin(admin.ModelAdmin):
    inlines = [
        MeterInline,
    ]


class EnergyConsumptionReportInline(admin.TabularInline):
    model = EnergyConsumptionReport


class MeterAdmin(admin.ModelAdmin):
    inlines = [
        EnergyConsumptionReportInline,
    ]
    list_filter = ['site__company__name', 'site__location', 'site__name']
    search_fields = ['meter_id', 'site__company__name', 'site__name', 'site__location__country']

# Register your models here.

admin.site.register(Company, CompanyAdmin)
admin.site.register(Site, SiteAdmin)
admin.site.register(Meter, MeterAdmin)
admin.site.register(ClientLog)
admin.site.register(SmeEmail)
