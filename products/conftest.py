import pytest

from products.pages.home_page import HomePage
from products.pages.product_page import ProductPage


@pytest.fixture
def home_page(page, settings) -> HomePage:
    return HomePage(page=page, settings=settings)


@pytest.fixture
def product_page(page, settings) -> ProductPage:
    return ProductPage(page=page, settings=settings)
