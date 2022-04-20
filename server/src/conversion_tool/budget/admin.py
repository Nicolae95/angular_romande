from django.contrib import admin
from .models import *


class BudgetRecordAdmin(admin.ModelAdmin):
    list_display = ('interval_start', 'budget')
    list_filter = ('interval_start', 'budget')
    search_fields = ('value', 'interval_start')


class BudgetMedSeasonRecordAdmin(admin.ModelAdmin):
    list_display = ('year', 'value', 'season', 'budget')
    list_filter = ('year', 'budget')
    search_fields = ('value', 'year')


class BudgetMedSeasonMajorationRecordAdmin(admin.ModelAdmin):
    list_display = ('year', 'value', 'season', 'budget')
    list_filter = ('year', 'budget')
    search_fields = ('value', 'year')


class BudgetMedSeasonRiscsRecordAdmin(admin.ModelAdmin):
    list_display = ('year', 'value', 'season', 'budget')
    list_filter = ('year', 'budget')
    search_fields = ('value', 'year')


class BudgetMedRecordAdmin(admin.ModelAdmin):
    list_display = ('year', 'value', 'budget')
    list_filter = ('year', 'budget')
    search_fields = ('value', 'year')

class BudgetMedRiscsRecordAdmin(admin.ModelAdmin):
    list_display = ('year', 'value', 'budget')
    list_filter = ('year', 'budget')
    search_fields = ('value', 'year')

class BudgetSeasonRecordAdmin(admin.ModelAdmin):
    list_display = ('value', 'year', 'season')
    list_filter = ('year', 'season')
    search_fields = ('value', 'year', 'season')


class BudgetWeeklyRecordAdmin(admin.ModelAdmin):
    list_display = ('value', 'hour', 'year')
    list_filter = ('year', 'hour')
    search_fields = ('value', 'hour', 'year')


class BudgetAverageCleanRecordAdmin(admin.ModelAdmin):
    list_display = ('value', 'year', 'budget')
    list_filter = ('year', 'budget')
    search_fields = ('value', 'year')



admin.site.register(Budget)
# admin.site.register(WeightedAverageRecord)
admin.site.register(BudgetAveragePerYear)
admin.site.register(BudgetAveragePerYearRiscs)
admin.site.register(BudgetAverageMajorationPerYear)
admin.site.register(BudgetAverageWithoutEfort)

admin.site.register(BudgetAverageClean, BudgetAverageCleanRecordAdmin)

# admin.site.register(BudgetRecord, BudgetRecordAdmin)
# admin.site.register(BudgetMedRecord, BudgetMedRecordAdmin)
# admin.site.register(BudgetMedWithRiscsRecord, BudgetMedRiscsRecordAdmin)
# admin.site.register(BudgetSeasonRecord, BudgetSeasonRecordAdmin)
admin.site.register(BudgetMedSeasonRecord, BudgetMedSeasonRecordAdmin)
admin.site.register(BudgetMedSeasonMajorationRecord, BudgetMedSeasonMajorationRecordAdmin)
admin.site.register(BudgetMedSeasonWithRiscsRecord, BudgetMedSeasonRiscsRecordAdmin)
