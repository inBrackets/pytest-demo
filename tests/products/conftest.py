import pytest

from products.pages.cart_page import CartPage
from products.pages.home_page import HomePage
from products.pages.product_detail_page import ProductDetailPage
from products.pages.product_page import ProductPage


@pytest.fixture
def home_page(page, settings) -> HomePage:
    return HomePage(page=page, settings=settings)


@pytest.fixture
def product_page(page, settings) -> ProductPage:
    return ProductPage(page=page, settings=settings)


@pytest.fixture
def product_detail_page(page, settings) -> ProductDetailPage:
    return ProductDetailPage(page=page, settings=settings)


@pytest.fixture
def cart_page(page, settings) -> CartPage:
    return CartPage(page=page, settings=settings)
