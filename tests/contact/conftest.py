import pytest

from contact.pages.contact_page import ContactPage


@pytest.fixture
def contact_page(page, settings) -> ContactPage:
    return ContactPage(page=page, settings=settings)
