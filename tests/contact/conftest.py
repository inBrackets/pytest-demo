import pytest
from playwright.sync_api import Page

from contact.pages.contact_page import ContactPage
from core.config import Settings


@pytest.fixture
def contact_page(page: Page, settings: Settings) -> ContactPage:
    return ContactPage(page=page, settings=settings)
