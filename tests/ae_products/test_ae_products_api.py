import allure
import pytest

from ae_products.api.ae_products_client import AeProductsClient


@allure.feature("AE Products API")
@allure.story("Get All Products")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.api
@pytest.mark.smoke
class TestGetAllProducts:
    """API 1 — GET /api/productsList"""

    def test_returns_200(self, ae_products_client: AeProductsClient) -> None:
        response = ae_products_client.get_all_products()
        assert response.response_code == 200

    def test_products_list_is_non_empty(self, ae_products_client: AeProductsClient) -> None:
        response = ae_products_client.get_all_products()
        assert len(response.products) > 0

    def test_each_product_has_name_and_price(self, ae_products_client: AeProductsClient) -> None:
        response = ae_products_client.get_all_products()
        for product in response.products:
            assert product.name
            assert product.price


@allure.feature("AE Products API")
@allure.story("Method Validation")
@allure.severity(allure.severity_level.MINOR)
@pytest.mark.api
class TestPostToProductsList:
    """API 2 — POST /api/productsList → 405"""

    def test_returns_405_method_not_supported(self, ae_products_client: AeProductsClient) -> None:
        response = ae_products_client.post_to_products_list()
        assert response.response_code == 405


@allure.feature("AE Products API")
@allure.story("Get All Brands")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.api
@pytest.mark.smoke
class TestGetAllBrands:
    """API 3 — GET /api/brandsList"""

    def test_returns_200(self, ae_products_client: AeProductsClient) -> None:
        response = ae_products_client.get_all_brands()
        assert response.response_code == 200

    def test_brands_list_is_non_empty(self, ae_products_client: AeProductsClient) -> None:
        response = ae_products_client.get_all_brands()
        assert len(response.brands) > 0


@allure.feature("AE Products API")
@allure.story("Method Validation")
@allure.severity(allure.severity_level.MINOR)
@pytest.mark.api
class TestPutToBrandsList:
    """API 4 — PUT /api/brandsList → 405"""

    def test_returns_405_method_not_supported(self, ae_products_client: AeProductsClient) -> None:
        response = ae_products_client.put_to_brands_list()
        assert response.response_code == 405


@allure.feature("AE Products API")
@allure.story("Search Products")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.api
@pytest.mark.smoke
class TestSearchProduct:
    """API 5 — POST /api/searchProduct"""

    def test_returns_matching_products(self, ae_products_client: AeProductsClient) -> None:
        response = ae_products_client.search_product("top")
        assert response.response_code == 200
        assert len(response.products) > 0

    def test_search_results_contain_keyword(self, ae_products_client: AeProductsClient) -> None:
        response = ae_products_client.search_product("Blue Top")
        assert any("Blue Top" in p.name for p in response.products)


@allure.feature("AE Products API")
@allure.story("Search Products — Various Keywords")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.api
class TestSearchProductVariousKeywords:
    """Verify search returns results across a range of common keywords."""

    @pytest.mark.parametrize("keyword", ["dress", "saree", "jeans"])
    def test_returns_results_for_keyword(
        self, ae_products_client: AeProductsClient, keyword: str
    ) -> None:
        response = ae_products_client.search_product(keyword)
        assert response.response_code == 200
        assert len(response.products) > 0, f"No results found for keyword '{keyword}'"


@allure.feature("AE Products API")
@allure.story("Search Products — Missing Parameter")
@allure.severity(allure.severity_level.MINOR)
@pytest.mark.api
class TestSearchProductMissingParam:
    """API 6 — POST /api/searchProduct without search_product → 400"""

    def test_returns_400_bad_request(self, ae_products_client: AeProductsClient) -> None:
        response = ae_products_client.search_product_missing_param()
        assert response.response_code == 400

    def test_error_message_mentions_missing_param(self, ae_products_client: AeProductsClient) -> None:
        response = ae_products_client.search_product_missing_param()
        assert "search_product" in response.message.lower()
