from django.contrib import admin
from .models import *
# Register your models here.




class RiscRecordAdmin(admin.ModelAdmin):
    list_display = ('risc', 'pfc', 'pfc_market', 'value', 'year')

    list_filter = ('risc', 'pfc', 'pfc_market', 'year')

    # def get_queryset(self, request):
    #     queryset = super(self.__class__, self).get_queryset(request)
    #     return queryset.select_related('pfc', 'pfc_market', 'value', 'year')


class ParameterRecordAdmin(admin.ModelAdmin):
    list_display = ('parameter', 'offer', 'value', 'year')

    list_filter = ('parameter', 'offer', 'year')

admin.site.register(Constants)
admin.site.register(Risc)
admin.site.register(RiscRecord, RiscRecordAdmin)
admin.site.register(Offer)
admin.site.register(OfferPlot)
admin.site.register(Parameter)
admin.site.register(ParameterRecord, ParameterRecordAdmin)
# admin.site.register(OfferHistory)
admin.site.register(GRD)
admin.site.register(GRDFile)

