import allure

from ae_products.models.ae_products_model import (
    AeBrandsResponse,
    AeMessageResponse,
    AeProductsResponse,
)
from core.ae_base_client import AeBaseClient


class AeProductsClient(AeBaseClient):
    @allure.step("GET /api/productsList")
    def get_all_products(self) -> AeProductsResponse:
        return AeProductsResponse.model_validate(self._get("/productsList"))

    @allure.step("POST /api/productsList")
    def post_to_products_list(self) -> AeMessageResponse:
        return AeMessageResponse.model_validate(self._post("/productsList"))

    @allure.step("GET /api/brandsList")
    def get_all_brands(self) -> AeBrandsResponse:
        return AeBrandsResponse.model_validate(self._get("/brandsList"))

    @allure.step("PUT /api/brandsList")
    def put_to_brands_list(self) -> AeMessageResponse:
        return AeMessageResponse.model_validate(self._put("/brandsList"))

    @allure.step("POST /api/searchProduct")
    def search_product(self, search_product: str) -> AeProductsResponse:
        return AeProductsResponse.model_validate(
            self._post("/searchProduct", form={"search_product": search_product})
        )

    @allure.step("POST /api/searchProduct — missing parameter")
    def search_product_missing_param(self) -> AeMessageResponse:
        return AeMessageResponse.model_validate(self._post("/searchProduct"))
