import allure
import pytest

from ae_account.api.ae_account_client import AeAccountClient
from ae_account.models.ae_account_model import AeCreateAccountRequest
from core.config import Settings


@allure.feature("AE Account API")
@allure.story("Verify Login")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.api
@pytest.mark.smoke
class TestVerifyLogin:
    """API 7 — POST /api/verifyLogin with valid credentials"""

    def test_returns_200_user_exists(
        self, ae_account_client: AeAccountClient, temp_account: dict[str, str]
    ) -> None:
        response = ae_account_client.verify_login(
            email=temp_account["email"],
            password=temp_account["password"],
        )
        assert response.response_code == 200

    def test_message_confirms_user_exists(
        self, ae_account_client: AeAccountClient, temp_account: dict[str, str]
    ) -> None:
        response = ae_account_client.verify_login(
            email=temp_account["email"],
            password=temp_account["password"],
        )
        assert "User exists" in response.message


@allure.feature("AE Account API")
@allure.story("Verify Login — Missing Parameters")
@allure.severity(allure.severity_level.MINOR)
@pytest.mark.api
class TestVerifyLoginMissingEmail:
    """API 8 — POST /api/verifyLogin without email → 400"""

    def test_returns_400_missing_parameter(
        self, ae_account_client: AeAccountClient, settings: Settings
    ) -> None:
        response = ae_account_client.verify_login_missing_email(
            password=settings.ae_password.get_secret_value()
        )
        assert response.response_code == 400


@allure.feature("AE Account API")
@allure.story("Method Validation")
@allure.severity(allure.severity_level.MINOR)
@pytest.mark.api
class TestDeleteVerifyLogin:
    """API 9 — DELETE /api/verifyLogin → 405"""

    def test_returns_405_method_not_supported(self, ae_account_client: AeAccountClient) -> None:
        response = ae_account_client.delete_verify_login()
        assert response.response_code == 405


@allure.feature("AE Account API")
@allure.story("Verify Login — Invalid Credentials")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.api
class TestVerifyLoginInvalidCredentials:
    """API 10 — POST /api/verifyLogin with invalid credentials → 404"""

    def test_returns_404_user_not_found(self, ae_account_client: AeAccountClient) -> None:
        response = ae_account_client.verify_login(
            email="nonexistent@example.com",
            password="wrongpassword",
        )
        assert response.response_code == 404

    def test_message_indicates_user_not_found(self, ae_account_client: AeAccountClient) -> None:
        response = ae_account_client.verify_login(
            email="nonexistent@example.com",
            password="wrongpassword",
        )
        assert "not found" in response.message.lower()


@allure.feature("AE Account API")
@allure.story("Create Account")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.api
class TestCreateAccount:
    """API 11 — POST /api/createAccount"""

    def test_returns_201_user_created(
        self, ae_account_client: AeAccountClient, disposable_credentials: dict[str, str]
    ) -> None:
        payload = AeCreateAccountRequest.make(
            name=disposable_credentials["name"],
            email=disposable_credentials["email"],
            password=disposable_credentials["password"],
        )
        response = ae_account_client.create_account(payload)
        assert response.response_code == 201

    def test_message_confirms_creation(
        self, ae_account_client: AeAccountClient, disposable_credentials: dict[str, str]
    ) -> None:
        payload = AeCreateAccountRequest.make(
            name=disposable_credentials["name"],
            email=disposable_credentials["email"],
            password=disposable_credentials["password"],
        )
        response = ae_account_client.create_account(payload)
        assert "created" in response.message.lower()


@allure.feature("AE Account API")
@allure.story("Delete Account")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.api
class TestDeleteAccount:
    """API 12 — DELETE /api/deleteAccount"""

    def test_returns_200_account_deleted(
        self, ae_account_client: AeAccountClient, temp_account: dict[str, str]
    ) -> None:
        response = ae_account_client.delete_account(
            email=temp_account["email"],
            password=temp_account["password"],
        )
        assert response.response_code == 200

    def test_message_confirms_deletion(
        self, ae_account_client: AeAccountClient, temp_account: dict[str, str]
    ) -> None:
        response = ae_account_client.delete_account(
            email=temp_account["email"],
            password=temp_account["password"],
        )
        assert "deleted" in response.message.lower()


@allure.feature("AE Account API")
@allure.story("Update Account")
@allure.severity(allure.severity_level.MINOR)
@pytest.mark.api
class TestUpdateAccount:
    """API 13 — PUT /api/updateAccount"""

    def test_returns_200_user_updated(
        self, ae_account_client: AeAccountClient, temp_account: dict[str, str]
    ) -> None:
        payload = AeCreateAccountRequest.make(
            name="Updated Name",
            email=temp_account["email"],
            password=temp_account["password"],
        )
        response = ae_account_client.update_account(payload)
        assert response.response_code == 200

    def test_message_confirms_update(
        self, ae_account_client: AeAccountClient, temp_account: dict[str, str]
    ) -> None:
        payload = AeCreateAccountRequest.make(
            name="Updated Name",
            email=temp_account["email"],
            password=temp_account["password"],
        )
        response = ae_account_client.update_account(payload)
        assert "updated" in response.message.lower()


@allure.feature("AE Account API")
@allure.story("Get User Detail")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.api
@pytest.mark.smoke
class TestGetUserDetail:
    """API 14 — GET /api/getUserDetailByEmail"""

    def test_returns_200_with_user_object(
        self, ae_account_client: AeAccountClient, settings: Settings
    ) -> None:
        response = ae_account_client.get_user_detail(email=settings.ae_username)
        assert response.response_code == 200

    def test_email_matches_requested(
        self, ae_account_client: AeAccountClient, settings: Settings
    ) -> None:
        response = ae_account_client.get_user_detail(email=settings.ae_username)
        assert response.user.email == settings.ae_username

    def test_user_has_required_fields(
        self, ae_account_client: AeAccountClient, settings: Settings
    ) -> None:
        response = ae_account_client.get_user_detail(email=settings.ae_username)
        user = response.user
        assert user.name
        assert user.id > 0
