import uuid
from typing import Generator

import pytest

from ae_account.api.ae_account_client import AeAccountClient
from ae_account.models.ae_account_model import AeCreateAccountRequest


@pytest.fixture
def ae_account_client(api_context, settings) -> AeAccountClient:
    return AeAccountClient(context=api_context, settings=settings)


@pytest.fixture
def temp_account(ae_account_client: AeAccountClient) -> Generator[dict, None, None]:
    email = f"pytest_{uuid.uuid4().hex[:8]}@test.com"
    password = "Test1234!"
    ae_account_client.create_account(
        AeCreateAccountRequest.make(email=email, password=password)
    )
    yield {"email": email, "password": password}
    try:
        ae_account_client.delete_account(email=email, password=password)
    except Exception:
        pass
