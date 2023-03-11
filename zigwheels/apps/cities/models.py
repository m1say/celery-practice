from django.db import models


class City(models.Model):
    external_id = models.CharField(max_length=20, null=True, blank=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=50)
    title = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = "cities"
