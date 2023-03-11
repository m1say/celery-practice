from django.contrib import admin

from .models import (
    Brand,
    BrandModel,
    CarFeature,
    ModelVariant,
)


admin.site.register(Brand)
admin.site.register(BrandModel)
admin.site.register(ModelVariant)
admin.site.register(CarFeature)
