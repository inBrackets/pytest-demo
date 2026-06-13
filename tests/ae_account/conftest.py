import pytest
from playwright.sync_api import APIRequestContext

from ae_account.api.ae_account_client import AeAccountClient
from core.config import Settings


@pytest.fixture
def ae_account_client(api_context: APIRequestContext, settings: Settings) -> AeAccountClient:
    return AeAccountClient(context=api_context, settings=settings)
