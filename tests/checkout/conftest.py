import pytest
from playwright.sync_api import APIRequestContext, Page

from ae_account.api.ae_account_client import AeAccountClient
from ae_account.models.ae_account_model import AeCreateAccountRequest
from core.config import Settings
from users.pages.login_page import LoginPage


@pytest.fixture
def registered_page(
    unauthenticated_page: Page,
    settings: Settings,
    disposable_credentials: dict[str, str],
    api_context: APIRequestContext,
) -> Page:
    """Page logged in with a freshly created temp account."""
    AeAccountClient(api_context, settings).create_account(
        AeCreateAccountRequest.make(
            name=disposable_credentials["name"],
            email=disposable_credentials["email"],
            password=disposable_credentials["password"],
        )
    )
    LoginPage(unauthenticated_page, settings).navigate().login(
        username=disposable_credentials["email"],
        password=disposable_credentials["password"],
    )
    if "/login" in unauthenticated_page.url:
        raise RuntimeError(
            f"Login failed for {disposable_credentials['email']} — "
            f"still at {unauthenticated_page.url!r}"
        )
    return unauthenticated_page
