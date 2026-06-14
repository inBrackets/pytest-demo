import allure
import pytest

from products.pages.product_page import ProductPage


@allure.feature("Product Catalog")
@allure.story("Category Navigation")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.ui
class TestViewCategoryProducts:
    """TC 18 — View Category Products"""

    def test_women_tops_category_shows_products(self, product_page: ProductPage) -> None:
        product_page.navigate()
        product_page.select_category("Women", "Tops")
        assert len(product_page.get_product_names()) > 0

    def test_men_tshirts_category_shows_products(self, product_page: ProductPage) -> None:
        product_page.navigate()
        product_page.select_category("Men", "Tshirts")
        assert len(product_page.get_product_names()) > 0


@allure.feature("Product Catalog")
@allure.story("Brand Navigation")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.ui
class TestViewBrandProducts:
    """TC 19 — View & Cart Brand Products"""

    def test_polo_brand_page_shows_products(self, product_page: ProductPage) -> None:
        product_page.navigate()
        product_page.click_brand("Polo")
        assert len(product_page.get_product_names()) > 0

    def test_h_m_brand_page_shows_products(self, product_page: ProductPage) -> None:
        product_page.navigate()
        product_page.click_brand("H&M")
        assert len(product_page.get_product_names()) > 0
