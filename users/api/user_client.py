import allure

from core.base_api_client import BaseApiClient
from users.models.user_model import CreateUserRequest, UserResponse


class UserApiClient(BaseApiClient[UserResponse]):
    endpoint = "/users"
    _response_model = UserResponse

    @property
    def base_url(self) -> str:
        return self._settings.api_base_url

    @allure.step("GET /users/{user_id}")
    def get(self, user_id: int) -> UserResponse:
        return self._get(user_id)

    @allure.step("GET /users")
    def get_all(self) -> list[UserResponse]:
        return self._get_many()

    @allure.step("POST /users")
    def create(self, payload: CreateUserRequest) -> UserResponse:
        return self._post(payload)

    @allure.step("PUT /users/{user_id}")
    def update(self, user_id: int, payload: CreateUserRequest) -> UserResponse:
        return self._put(user_id, payload)

    @allure.step("DELETE /users/{user_id}")
    def delete(self, user_id: int) -> None:
        self._delete(user_id)
