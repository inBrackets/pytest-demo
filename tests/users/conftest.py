import pytest

from users.api.user_client import UserApiClient
from users.pages.login_page import LoginPage


@pytest.fixture
def user_client(api_context, settings) -> UserApiClient:
    return UserApiClient(context=api_context, settings=settings)


@pytest.fixture
def login_page(page, settings) -> LoginPage:
    return LoginPage(page=page, settings=settings)
