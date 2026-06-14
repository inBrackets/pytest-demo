import allure
import pytest
from playwright.sync_api import Page, expect

from core.config import Settings
from products.pages.home_page import HomePage
from products.pages.product_page import ProductPage


@allure.feature("Product UI")
@allure.story("Visual Regression")
@pytest.mark.ui
@pytest.mark.visual
class TestProductVisualRegression:
    def test_home_page_hero_banner(self, unauthenticated_page: Page, settings: Settings) -> None:
        HomePage(page=unauthenticated_page, settings=settings).navigate()
        expect(unauthenticated_page.locator(".item.active").first).to_be_visible()

    def test_product_listing_grid(self, unauthenticated_page: Page, settings: Settings) -> None:
        ProductPage(page=unauthenticated_page, settings=settings).navigate()
        expect(unauthenticated_page.locator(".features_items")).to_be_visible()
