import allure
import pytest

from products.pages.home_page import HomePage
from products.pages.product_page import ProductPage


@allure.feature("Product Catalog")
@allure.story("Product Listing")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.ui
@pytest.mark.smoke
class TestProductPage:
    def test_page_loads(self, product_page: ProductPage) -> None:
        product_page.navigate()

    def test_products_are_listed(self, product_page: ProductPage) -> None:
        product_page.navigate()
        names = product_page.get_product_names()
        assert len(names) > 0


@allure.feature("Product Catalog")
@allure.story("Product Search")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ui
class TestProductSearch:
    def test_search_returns_results(self, product_page: ProductPage) -> None:
        product_page.navigate()
        product_page.search("Blue Top")
        names = product_page.get_product_names()
        assert len(names) > 0
