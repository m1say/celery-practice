import logging

import requests
from requests import HTTPError
from requests.adapters import HTTPAdapter
from urllib3 import Retry


logger = logging.getLogger(__name__)


def raise_and_log_error(response, *args, **kwargs):
    try:
        response.raise_for_status()
    except HTTPError:
        logger.exception(
            "Got response with status code {}: {}".format(
                response.status_code, response.text
            )
        )
        raise
    return response


class ZigWheelsAPI:
    def __init__(self, host="", version="v1"):
        self.host = host or "https://newcarsapi.carbay.com"
        self.version = version

        session = requests.Session()
        session.hooks["response"] = [raise_and_log_error]

        retry_strategy = Retry(
            total=3,
            status_forcelist=[500, 503],
            allowed_methods=["GET"],
            backoff_factor=2,
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount(self.host, adapter)
        self.session = session

    def construct_params(self, params):
        _params = params or {}
        _params.update(
            {"business_unit": "car", "lang_code": "en", "country_code": "ph"}
        )
        return _params

    def run(self, method="GET", endpoint="", **kwargs):
        url = f"{self.host}/{self.version}/{endpoint}"
        kwargs["params"] = self.construct_params(kwargs.get("params", None))

        response = self.session.request(method, url, **kwargs)
        return response.json()["data"]

    def get_car_brands(self):
        data = self.run(
            method="GET",
            endpoint="brand/index",
        )
        return data

    def get_brand_models(self, brand_id, is_expired=1, model_status="launched"):
        if brand_id is None:
            return []

        data = self.run(
            method="GET",
            endpoint="brand/models",
            params={
                "id": brand_id,
                "isExpired": is_expired,
                "modelStatus": model_status,
            },
        )
        return data

    def get_model_variants(self, model_id, is_expired=1):
        if model_id is None:
            return []

        data = self.run(
            method="GET",
            endpoint="model/variants",
            params={"modelId": model_id, "isExpired": is_expired},
        )
        return data

    def get_model_variant_overview(self, model_id, variant_id, format_price="0"):
        if not any([model_id, variant_id]):
            return []

        data = self.run(
            method="GET",
            endpoint="model/overview",
            params={
                "modelId": model_id,
                "variantId": variant_id,
                "formatPrice": format_price,
            },
        )
        return data


if __name__ == "__main__":
    import json

    api_client = ZigWheelsAPI()
    brands = api_client.get_car_brands()
    brand_models = api_client.get_brand_models(brand_id=30)
    model_variants = api_client.get_model_variants(model_id=1943)
    model_variant_overview = api_client.get_model_variant_overview(
        model_id=1943, variant_id=4069
    )
    # print(json.dumps(model_variant_overview, default=str, indent=2))
    print(f"{len(brands)=} {len(brand_models)=} {len(model_variants)=}")
