import allure

from core.base_api_client import BaseApiClient
from posts.models.post_model import CreatePostRequest, PostResponse


class PostApiClient(BaseApiClient[PostResponse]):
    endpoint = "/posts"
    _response_model = PostResponse

    @property
    def base_url(self) -> str:
        return self._settings.api_base_url

    @allure.step("GET /posts/{post_id}")
    def get(self, post_id: int) -> PostResponse:
        return self._get(post_id)

    @allure.step("GET /posts")
    def get_all(self) -> list[PostResponse]:
        return self._get_many()

    @allure.step("POST /posts")
    def create(self, payload: CreatePostRequest) -> PostResponse:
        return self._post(payload)

    @allure.step("PUT /posts/{post_id}")
    def update(self, post_id: int, payload: CreatePostRequest) -> PostResponse:
        return self._put(post_id, payload)

    @allure.step("DELETE /posts/{post_id}")
    def delete(self, post_id: int) -> None:
        self._delete(post_id)
