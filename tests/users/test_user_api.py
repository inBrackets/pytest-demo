import allure
import pytest

from core.exceptions import ApiError
from users.api.user_client import UserApiClient
from users.models.user_model import CreateUserRequest


@allure.feature("Users API")
@allure.story("Retrieve User by ID")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.api
@pytest.mark.smoke
class TestGetUser:
    def test_returns_valid_schema(self, user_client: UserApiClient) -> None:
        user = user_client.get(user_id=1)
        assert user.id == 1

    def test_name_is_non_empty(self, user_client: UserApiClient) -> None:
        user = user_client.get(user_id=1)
        assert user.name

    def test_unknown_id_raises_api_error(self, user_client: UserApiClient) -> None:
        with pytest.raises(ApiError) as exc:
            user_client.get(user_id=9999)
        assert exc.value.status_code == 404

    @pytest.mark.parametrize("user_id", [1, 3, 5, 7, 10])
    def test_valid_id_returns_matching_user(
        self, user_client: UserApiClient, user_id: int
    ) -> None:
        user = user_client.get(user_id=user_id)
        assert user.id == user_id
        assert user.name
        assert user.email


@allure.feature("Users API")
@allure.story("Retrieve All Users")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.api
class TestGetAllUsers:
    def test_returns_non_empty_list(self, user_client: UserApiClient) -> None:
        users = user_client.get_all()
        assert len(users) > 0

    def test_all_items_have_id(self, user_client: UserApiClient) -> None:
        users = user_client.get_all()
        assert all(u.id > 0 for u in users)


@allure.feature("Users API")
@allure.story("Create User")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.api
class TestCreateUser:
    def test_echoes_payload_fields(self, user_client: UserApiClient) -> None:
        payload = CreateUserRequest.make(name="Alice", email="alice@example.com")
        user = user_client.create(payload)
        assert user.name == "Alice"
        assert user.email == "alice@example.com"

    def test_response_includes_generated_id(self, user_client: UserApiClient) -> None:
        user = user_client.create(CreateUserRequest.make())
        assert user.id > 0

    @pytest.mark.parametrize("name,email", [
        ("Alice Smith", "alice@example.com"),
        ("Bob O'Brien", "bob@example.com"),
        ("María García", "maria@example.com"),
    ])
    def test_various_names_are_echoed(
        self, user_client: UserApiClient, name: str, email: str
    ) -> None:
        user = user_client.create(CreateUserRequest.make(name=name, email=email))
        assert user.name == name
        assert user.email == email


@allure.feature("Users API")
@allure.story("Update User")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.api
class TestUpdateUser:
    def test_updated_name_is_reflected(self, user_client: UserApiClient) -> None:
        payload = CreateUserRequest.make(name="Updated Name")
        user = user_client.update(user_id=1, payload=payload)
        assert user.name == "Updated Name"


@allure.feature("Users API")
@allure.story("Delete User")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.api
class TestDeleteUser:
    def test_delete_returns_none(self, user_client: UserApiClient) -> None:
        result = user_client.delete(user_id=1)
        assert result is None
