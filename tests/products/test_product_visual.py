from typing import Callable, Union

import allure
import pytest
from playwright.sync_api import Locator, Page

from core.config import Settings
from products.pages.home_page import HomePage
from products.pages.product_page import ProductPage

# Pixels allowed to differ between runs — absorbs minor CDN/font rendering variance
# without masking real layout regressions (a moved element changes thousands of pixels).
_PIXEL_TOLERANCE = 4000


@allure.feature("Product UI")
@allure.story("Pixel Snapshot Regression")
@allure.severity(allure.severity_level.MINOR)
@pytest.mark.ui
@pytest.mark.visual
class TestProductPixelSnapshots:
    """Layout regression using locator screenshots with a small pixel tolerance.

    Create / update baselines (re-run after intentional UI changes):
        uv run pytest tests/products/test_product_visual.py --update-snapshots

    Normal run — fails if more than _PIXEL_TOLERANCE pixels differ from the baseline:
        uv run pytest tests/products/test_product_visual.py

    Baselines are stored in tests/products/__snapshots__/ and must be committed to git.
    """

    def test_home_navbar_snapshot(
        self,
        unauthenticated_page: Page,
        settings: Settings,
        assert_snapshot: Callable[[Union[Locator, Page], str, int], None],
    ) -> None:
        HomePage(page=unauthenticated_page, settings=settings).navigate()
        assert_snapshot(
            unauthenticated_page.locator("#header"),
            "home-navbar.png",
            _PIXEL_TOLERANCE,
        )

    def test_all_products_heading_snapshot(
        self,
        unauthenticated_page: Page,
        settings: Settings,
        assert_snapshot: Callable[[Union[Locator, Page], str, int], None],
    ) -> None:
        ProductPage(page=unauthenticated_page, settings=settings).navigate()
        assert_snapshot(
            unauthenticated_page.locator("h2", has_text="All Products"),
            "all-products-heading.png",
            _PIXEL_TOLERANCE,
        )
