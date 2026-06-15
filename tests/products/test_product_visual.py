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

    def test_home_navbar_snapshot(
        self,
        unauthenticated_page: Page,
        settings: Settings,
        assert_snapshot: Callable[[Union[Locator, Page], str], None],
    ) -> None:
        HomePage(page=unauthenticated_page, settings=settings).navigate()
        # Screenshot the site header — stable, static element (excludes the rotating carousel).
        assert_snapshot(unauthenticated_page.locator("#header"), "home-navbar.png")

    def test_all_products_heading_snapshot(
        self,
        unauthenticated_page: Page,
        settings: Settings,
        assert_snapshot: Callable[[Union[Locator, Page], str], None],
    ) -> None:
        ProductPage(page=unauthenticated_page, settings=settings).navigate()
        # Screenshot the heading section — static text with no dynamic images.
        assert_snapshot(unauthenticated_page.locator("h2", has_text="All Products"), "all-products-heading.png")
