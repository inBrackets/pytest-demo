from typing import Callable, Union

import allure
import pytest
from playwright.sync_api import Locator, Page

from core.config import Settings
from products.pages.home_page import HomePage
from products.pages.product_page import ProductPage


@allure.feature("Product UI")
@allure.story("Pixel Snapshot Regression")
@allure.severity(allure.severity_level.MINOR)
@pytest.mark.ui
@pytest.mark.visual
class TestProductPixelSnapshots:
    """Pixel-for-pixel layout regression using locator screenshots.

    Create / update baselines (re-run after intentional UI changes):
        uv run pytest tests/products/test_product_visual.py --update-snapshots

    Normal run — fails if pixels differ from the stored baseline:
        uv run pytest tests/products/test_product_visual.py

    Baselines are stored in tests/products/__snapshots__/ and must be committed to git.
    """

    def test_home_hero_snapshot(
        self,
        unauthenticated_page: Page,
        settings: Settings,
        assert_snapshot: Callable[[Union[Locator, Page], str], None],
    ) -> None:
        HomePage(page=unauthenticated_page, settings=settings).navigate()
        # Screenshot the full viewport — the hero carousel uses CSS transitions that
        # make .item.active not visible to Playwright's locator screenshot API.
        assert_snapshot(unauthenticated_page, "home-hero-banner.png")

    def test_product_listing_and_card_snapshots(
        self,
        unauthenticated_page: Page,
        settings: Settings,
        assert_snapshot: Callable[[Union[Locator, Page], str], None],
    ) -> None:
        ProductPage(page=unauthenticated_page, settings=settings).navigate()
        assert_snapshot(unauthenticated_page.locator(".features_items"), "product-listing-grid.png")
        assert_snapshot(unauthenticated_page.locator(".productinfo").first, "product-card.png")
