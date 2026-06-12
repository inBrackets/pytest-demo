import pytest

from core.exceptions import ApiError
from posts.api.post_client import PostApiClient
from posts.models.post_model import CreatePostRequest


@pytest.mark.api
@pytest.mark.smoke
class TestGetPost:
    def test_returns_valid_schema(self, post_client: PostApiClient) -> None:
        post = post_client.get(post_id=1)
        assert post.id == 1

    def test_user_id_is_positive(self, post_client: PostApiClient) -> None:
        post = post_client.get(post_id=1)
        assert post.user_id > 0

    def test_title_is_non_empty(self, post_client: PostApiClient) -> None:
        post = post_client.get(post_id=1)
        assert post.title

    def test_unknown_id_raises_api_error(self, post_client: PostApiClient) -> None:
        with pytest.raises(ApiError) as exc:
            post_client.get(post_id=9999)
        assert exc.value.status_code == 404


@pytest.mark.api
class TestGetAllPosts:
    def test_returns_non_empty_list(self, post_client: PostApiClient) -> None:
        posts = post_client.get_all()
        assert len(posts) > 0

    def test_user_id_deserializes_from_camel_case(self, post_client: PostApiClient) -> None:
        posts = post_client.get_all()
        assert all(p.user_id > 0 for p in posts)


@pytest.mark.api
class TestCreatePost:
    def test_echoes_payload_fields(self, post_client: PostApiClient) -> None:
        payload = CreatePostRequest.make(title="Hello World")
        post = post_client.create(payload)
        assert post.title == "Hello World"

    def test_response_includes_generated_id(self, post_client: PostApiClient) -> None:
        post = post_client.create(CreatePostRequest.make())
        assert post.id > 0
