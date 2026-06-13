import pytest

from ae_products.api.ae_products_client import AeProductsClient


@pytest.fixture
def ae_products_client(api_context, settings) -> AeProductsClient:
    return AeProductsClient(context=api_context, settings=settings)
