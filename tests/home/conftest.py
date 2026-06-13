import pytest

from products.pages.home_page import HomePage


@pytest.fixture
def home_page(page, settings) -> HomePage:
    return HomePage(page=page, settings=settings)
