import pytest

from products.pages.product_detail_page import ProductDetailPage
from products.pages.product_page import ProductPage


@pytest.mark.ui
@pytest.mark.smoke
class TestProductDetailPage:
    """TC 8 — Verify All Products and Product Detail Page"""

    def test_product_detail_page_shows_name(self, product_detail_page: ProductDetailPage) -> None:
        product_detail_page.navigate_to(product_id=1)
        assert product_detail_page.get_name()

    def test_product_detail_page_shows_price(self, product_detail_page: ProductDetailPage) -> None:
        product_detail_page.navigate_to(product_id=1)
        assert product_detail_page.get_price()

    def test_product_detail_page_shows_category(self, product_detail_page: ProductDetailPage) -> None:
        product_detail_page.navigate_to(product_id=1)
        assert "Category" in product_detail_page.get_category()

    def test_product_detail_page_shows_availability(self, product_detail_page: ProductDetailPage) -> None:
        product_detail_page.navigate_to(product_id=1)
        assert "Availability" in product_detail_page.get_availability()

    def test_product_detail_page_shows_brand(self, product_detail_page: ProductDetailPage) -> None:
        product_detail_page.navigate_to(product_id=1)
        assert "Brand" in product_detail_page.get_brand()

    def test_view_product_link_navigates_to_detail(
        self, product_page: ProductPage, product_detail_page: ProductDetailPage
    ) -> None:
        product_page.navigate()
        product_page.click_view_product(index=0)
        product_detail_page.is_loaded()


@pytest.mark.ui
class TestAddReview:
    """TC 21 — Add Review on Product"""

    def test_review_submission_shows_success(self, product_detail_page: ProductDetailPage) -> None:
        product_detail_page.navigate_to(product_id=1)
        product_detail_page.submit_review(
            name="Pytest Reviewer",
            email="review@test.com",
            review="Great product, automated test review.",
        )
