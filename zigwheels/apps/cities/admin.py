from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import City


class CityAdmin(ModelAdmin):
    list_display = ["name", "title"]


admin.site.register(City, CityAdmin)
