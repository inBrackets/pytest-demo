import pytest

from posts.api.post_client import PostApiClient


@pytest.fixture
def post_client(api_context, settings) -> PostApiClient:
    return PostApiClient(context=api_context, settings=settings)
