import pytest
from playwright.sync_api import APIRequestContext

from ae_products.api.ae_products_client import AeProductsClient
from core.config import Settings


@pytest.fixture
def ae_products_client(api_context: APIRequestContext, settings: Settings) -> AeProductsClient:
    return AeProductsClient(context=api_context, settings=settings)
