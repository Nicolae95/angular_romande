from django.contrib import admin
from .models import *

class TranslationRecordAdmin(admin.ModelAdmin):
    list_display = ('interval_start', 'value', 'meter')
    list_filter = ('interval_start', 'meter')
    search_fields = ('value', 'interval_start')

admin.site.register(Translation)
admin.site.register(TranslationRecord, TranslationRecordAdmin)
