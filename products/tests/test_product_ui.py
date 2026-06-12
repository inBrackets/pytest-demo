import pytest

from products.pages.home_page import HomePage
from products.pages.product_page import ProductPage


@pytest.mark.ui
@pytest.mark.smoke
class TestProductPage:
    def test_page_loads(self, product_page: ProductPage) -> None:
        product_page.navigate()

    def test_products_are_listed(self, product_page: ProductPage) -> None:
        product_page.navigate()
        names = product_page.get_product_names()
        assert len(names) > 0


@pytest.mark.ui
class TestHomePageSearch:
    def test_search_navigates_to_results(self, home_page: HomePage) -> None:
        home_page.navigate()
        home_page.search("Blue Top")
        assert "search" in home_page._page.url
