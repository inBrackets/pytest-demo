import pytest
from playwright.sync_api import APIRequestContext

from core.config import Settings
from users.api.user_client import UserApiClient


@pytest.fixture
def user_client(api_context: APIRequestContext, settings: Settings) -> UserApiClient:
    return UserApiClient(context=api_context, settings=settings)
