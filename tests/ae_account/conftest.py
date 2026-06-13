import pytest

from ae_account.api.ae_account_client import AeAccountClient


@pytest.fixture
def ae_account_client(api_context, settings) -> AeAccountClient:
    return AeAccountClient(context=api_context, settings=settings)
