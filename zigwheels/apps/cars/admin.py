from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import (
    Brand,
    Car,
    CarFeature,
    CarVariant,
)


class CarAdmin(ModelAdmin):
    list_display = ["brand", "name"]
    list_filter = ("brand",)
    list_select_related = ["brand"]


class CarFeatureAdmin(ModelAdmin):
    list_display = ["name", "value", "unit", "type"]


class CarVariantAdmin(ModelAdmin):
    list_display = ["parent", "name"]
    list_select_related = ["parent"]


admin.site.register(Brand)
admin.site.register(Car, CarAdmin)
admin.site.register(CarFeature, CarFeatureAdmin)
admin.site.register(CarVariant, CarVariantAdmin)
