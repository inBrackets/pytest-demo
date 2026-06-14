"""
Visual regression tests using Playwright's built-in snapshot comparison.

First-time setup — generate baselines before running:
    uv run pytest tests/products/test_product_visual.py --update-snapshots

Baselines are stored in tests/products/__snapshots__/ and should be committed.
Subsequent runs compare against those baselines with the given pixel tolerance.
To exclude from a normal test run: pytest -m "not visual"
"""
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
    def test_home_page_hero_banner(self, page: Page, settings: Settings) -> None:
        """Hero banner must not drift visually between runs."""
        HomePage(page=page, settings=settings).navigate()
        expect(page.locator(".item.active")).to_have_screenshot(
            "home-hero.png",
            threshold=0.1,
        )

    def test_product_listing_grid(self, page: Page, settings: Settings) -> None:
        """Product grid layout must stay consistent."""
        ProductPage(page=page, settings=settings).navigate()
        expect(page.locator(".features_items")).to_have_screenshot(
            "product-listing.png",
            threshold=0.1,
        )
