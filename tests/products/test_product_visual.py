import allure
import pytest
from playwright.sync_api import Page, expect

from core.config import Settings
from products.pages.home_page import HomePage
from products.pages.product_page import ProductPage


@allure.feature("Product UI")
@allure.story("Pixel Snapshot Regression")
@allure.severity(allure.severity_level.MINOR)
@pytest.mark.ui
@pytest.mark.visual
class TestProductPixelSnapshots:
    """Pixel-for-pixel layout regression using Playwright's built-in screenshot comparison.

    Create / update baselines (re-run after intentional UI changes):
        uv run pytest tests/products/test_product_visual.py::TestProductPixelSnapshots --update-snapshots

    Normal run — fails if pixels differ beyond the built-in tolerance:
        uv run pytest tests/products/test_product_visual.py::TestProductPixelSnapshots

    Baselines are stored in tests/products/__snapshots__/ and must be committed to git.
    """

    def test_home_hero_snapshot(self, unauthenticated_page: Page, settings: Settings) -> None:
        HomePage(page=unauthenticated_page, settings=settings).navigate()
        expect(unauthenticated_page.locator(".item.active").first).to_have_screenshot(
            "home-hero-banner.png"
        )

    def test_product_listing_and_card_snapshots(self, unauthenticated_page: Page, settings: Settings) -> None:
        ProductPage(page=unauthenticated_page, settings=settings).navigate()
        expect(unauthenticated_page.locator(".features_items")).to_have_screenshot(
            "product-listing-grid.png"
        )
        expect(unauthenticated_page.locator(".productinfo").first).to_have_screenshot(
            "product-card.png"
        )
