import pytest
from playwright.sync_api import Page

from core.config import Settings
from products.pages.cart_page import CartPage
from products.pages.product_detail_page import ProductDetailPage
from products.pages.product_page import ProductPage


@pytest.fixture
def product_page(page: Page, settings: Settings) -> ProductPage:
    return ProductPage(page=page, settings=settings)


@pytest.fixture
def product_detail_page(page: Page, settings: Settings) -> ProductDetailPage:
    return ProductDetailPage(page=page, settings=settings)


@pytest.fixture
def cart_page(page: Page, settings: Settings) -> CartPage:
    return CartPage(page=page, settings=settings)
