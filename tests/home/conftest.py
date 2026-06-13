import pytest
from playwright.sync_api import Page

from core.config import Settings
from products.pages.home_page import HomePage


@pytest.fixture
def home_page(page: Page, settings: Settings) -> HomePage:
    return HomePage(page=page, settings=settings)
