import logging
from datetime import datetime

from celery import group
from django.db.utils import IntegrityError
from djmoney.money import Money

from config.celery import app
from zigwheels.apps.api.api_client import ZigWheelsAPI
from zigwheels.apps.cars.models import (
    Brand,
    Car,
    CarFeature,
    CarVariant,
)
from zigwheels.apps.cities.models import City


logger = logging.getLogger(__name__)


# TODO: add retry strategy


@app.task(bind=True)
def download_cities(self):
    api_client = ZigWheelsAPI()
    results = api_client.get_cities()
    logger.info(f"Fetched {len(results)} from API.")

    # TODO: bulk create
    #   bulk update with selected fields
    for idx, result in enumerate(results, start=1):
        city, _created = City.objects.update_or_create(
            external_id=result["id"],
            defaults={
                "name": result["name"],
                "slug": result["slug"],
                "title": result["title"],
            },
        )
        if _created:
            logger.debug(f"Created City(name={result['name']}) -- {idx}/{len(results)}")
        else:
            logger.debug(f"Updated City(name={result['name']})-- {idx}/{len(results)}")


@app.task(bind=True)
def download_car_brands(self):
    api_client = ZigWheelsAPI()
    results = api_client.get_car_brands()
    logger.info(f"Fetched {len(results)} from API.")
    for idx, result in enumerate(results, start=1):
        brand, _created = Brand.objects.update_or_create(
            external_id=result["id"],
            defaults={
                "name": result["name"],
                "slug": result["slug"],
            },
        )
        if _created:
            logger.debug(
                f"Created Brand(name={result['name']}) -- {idx}/{len(results)}"
            )
        else:
            logger.debug(f"Updated Brand(name={result['name']})-- {idx}/{len(results)}")


@app.task(bind=True)
def download_car_models(self):
    # TODO: use group tasks
    api_client = ZigWheelsAPI()
    for brand in Brand.objects.all():
        logger.debug(f"Processing brand {brand.name}")
        results = api_client.get_brand_models(brand_id=brand.pk)
        logger.info(f"Fetched {len(results)} from API.")
        for idx, result in enumerate(results, start=1):
            car, _created = Car.objects.update_or_create(
                external_id=result["id"],
                brand_id=brand.pk,
                defaults={
                    "name": result["name"],
                },
            )
            if _created:
                logger.debug(
                    f"Created {brand.name} Car(name={result['name']}) -- {idx}/{len(results)}"
                )
            else:
                logger.debug(
                    f"Updated Car(name={result['name']})-- {idx}/{len(results)}"
                )


@app.task(bind=True)
def download_car_variants(self):
    tasks = [
        download_car_variants_batch.si(model_id=car.pk) for car in Car.objects.all()
    ]
    group(*tasks).apply_async(serializer="json")


@app.task(bind=True)
def download_car_variants_batch(self, model_id):
    api_client = ZigWheelsAPI()

    results = api_client.get_model_variants(model_id=model_id)
    for idx, result in enumerate(results, start=1):
        overview = api_client.get_model_variant_overview(
            model_id=model_id, variant_id=result["id"]
        )
        features = []
        for feature in result["keyFeatures"]:
            car_kwargs = {
                "name": feature["name"],
                "value": feature["value"],
                "unit": feature["unit"],
                "type": feature["groupName"],
            }
            try:
                car_feature = CarFeature.objects.create(**car_kwargs)
            except IntegrityError:
                car_feature = CarFeature.objects.get(**car_kwargs)
            features.append(car_feature)

        variant, _created = CarVariant.objects.update_or_create(
            external_id=result["id"],
            parent_id=model_id,
            defaults={
                "name": result["variant"],
                "slug": result["variantSlug"],
                "vehicle_type": result["vehicleType"],
                "fuel_type": result["fuelType"],
                "body_type": result["bodyType"],
                "launched": datetime.fromtimestamp(int(result["launchedTimestamp"])),
                "min_price": Money(overview["minPrice"], "PHP"),
                "max_price": Money(overview["maxPrice"], "PHP"),
                "raw_data": overview,
            },
        )
        variant.features.set(features)

        if _created:
            logger.debug(
                f"Created Variant(name={result['name']}id={variant.id}) -- {idx}/{len(results)}"
            )
        else:
            logger.debug(
                f"Updated Variant(name={result['name']} id={variant.id}) -- {idx}/{len(results)}"
            )

    return len(results)
