import pytest
from playwright.sync_api import APIRequestContext, Page

from core.config import Settings
from users.api.user_client import UserApiClient
from users.pages.login_page import LoginPage


@pytest.fixture
def user_client(api_context: APIRequestContext, settings: Settings) -> UserApiClient:
    return UserApiClient(context=api_context, settings=settings)


@pytest.fixture
def login_page(page: Page, settings: Settings) -> LoginPage:
    return LoginPage(page=page, settings=settings)
