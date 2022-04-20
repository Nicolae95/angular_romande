from django.contrib import admin

# Register your models here.

from geo.models import Location, Region, Holiday, HolidayFile

admin.site.register(Location)
admin.site.register(Region)
admin.site.register(Holiday)
admin.site.register(HolidayFile)
