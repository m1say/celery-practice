from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.translation import gettext_lazy as _
from djmoney.models.fields import MoneyField
from model_utils.models import TimeStampedModel


class BaseModel(TimeStampedModel):
    external_id = models.CharField(
        _("External identifier"), max_length=100, db_index=True
    )

    class Meta:
        abstract = True


class Brand(BaseModel):
    name = models.CharField(_("Brand name"), max_length=100, blank=True)
    slug = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name


class Car(BaseModel):
    name = models.CharField(_("Car model"), max_length=100, blank=True)
    brand = models.ForeignKey(Brand, related_name="models", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.brand.name} - {self.name}"


class CarFeature(BaseModel):
    name = models.CharField(
        _("Car feature"),
        max_length=100,
        blank=True,
        help_text=_("Name of the car feature"),
    )
    value = models.CharField(
        _("value"), max_length=100, help_text=_("Value of the car feature")
    )
    unit = models.CharField(
        _("unit"),
        max_length=50,
        blank=True,
        help_text=_("Unit of the car feature value"),
    )
    type = models.CharField(
        _("Car feature type"),
        max_length=50,
        blank=True,
        help_text=_("Type/Category of car feature"),
    )

    class Meta:
        unique_together = ["name", "value", "unit"]

    def __str__(self):
        return f"{self.name} - {self.value} {self.unit}"


class CarVariant(BaseModel):
    parent = models.ForeignKey(Car, related_name="variants", on_delete=models.CASCADE)
    name = models.CharField(
        _("Car variant name"),
        max_length=100,
        blank=True,
    )
    slug = models.SlugField(max_length=50)
    vehicle_type = models.CharField(
        _("Car vehicle type"),
        max_length=50,
        blank=True,
    )
    fuel_type = models.CharField(
        _("Car fuel type"),
        max_length=50,
        blank=True,
    )
    body_type = models.CharField(
        _("Car body type"),
        max_length=50,
        blank=True,
    )
    launched = models.DateField(_("Launch date"))
    features = models.ManyToManyField(CarFeature, related_name="cars", blank=True)
    min_price = MoneyField(max_digits=19, decimal_places=2, default_currency="PHP")
    max_price = MoneyField(max_digits=19, decimal_places=2, default_currency="PHP")
    raw_data = models.JSONField(blank=True, default=dict, encoder=DjangoJSONEncoder)

    @property
    def price_range(self):
        return f"{self.min_price} - {self.max_price}"
