import pytest
from playwright.sync_api import APIRequestContext

from core.config import Settings
from posts.api.post_client import PostApiClient


@pytest.fixture
def post_client(api_context: APIRequestContext, settings: Settings) -> PostApiClient:
    return PostApiClient(context=api_context, settings=settings)
