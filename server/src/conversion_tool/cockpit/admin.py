from django.contrib import admin
from .models import *

admin.site.register(Cockpit)
admin.site.register(CockpitOffer)

admin.site.register(CockpitNews)
admin.site.register(NewsCategory)
admin.site.register(News)
admin.site.register(CockpitMarket)
admin.site.register(Chart)
