import allure
import pytest

from core.exceptions import ApiError
from posts.api.post_client import PostApiClient
from posts.models.post_model import CreatePostRequest


@allure.feature("Posts API")
@allure.story("Retrieve Post by ID")
@allure.severity(allure.severity_level.CRITICAL)
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

    @pytest.mark.parametrize("post_id", [1, 25, 50, 75, 100])
    def test_valid_id_returns_matching_post(
        self, post_client: PostApiClient, post_id: int
    ) -> None:
        post = post_client.get(post_id=post_id)
        assert post.id == post_id
        assert post.title
        assert post.body


@allure.feature("Posts API")
@allure.story("Retrieve All Posts")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.api
class TestGetAllPosts:
    def test_returns_non_empty_list(self, post_client: PostApiClient) -> None:
        posts = post_client.get_all()
        assert len(posts) > 0

    def test_user_id_deserializes_from_camel_case(self, post_client: PostApiClient) -> None:
        posts = post_client.get_all()
        assert all(p.user_id > 0 for p in posts)


@allure.feature("Posts API")
@allure.story("Create Post")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.api
class TestCreatePost:
    def test_echoes_payload_fields(self, post_client: PostApiClient) -> None:
        payload = CreatePostRequest.make(title="Hello World")
        post = post_client.create(payload)
        assert post.title == "Hello World"

    def test_response_includes_generated_id(self, post_client: PostApiClient) -> None:
        post = post_client.create(CreatePostRequest.make())
        assert post.id > 0

    @pytest.mark.parametrize("title,body", [
        ("Short", "Brief content."),
        ("A" * 80, "Body with a maximum-length title."),
        ("Unicode: café 北京", "Body content with unicode characters."),
    ])
    def test_various_payloads_return_generated_id(
        self, post_client: PostApiClient, title: str, body: str
    ) -> None:
        post = post_client.create(CreatePostRequest.make(title=title, body=body))
        assert post.id > 0
        assert post.title == title
        assert post.body == body


@allure.feature("Posts API")
@allure.story("Update Post")
@allure.severity(allure.severity_level.MINOR)
@pytest.mark.api
class TestUpdatePost:
    def test_updated_title_is_reflected(self, post_client: PostApiClient) -> None:
        payload = CreatePostRequest.make(title="Updated Title")
        post = post_client.update(post_id=1, payload=payload)
        assert post.title == "Updated Title"


@allure.feature("Posts API")
@allure.story("Delete Post")
@allure.severity(allure.severity_level.MINOR)
@pytest.mark.api
class TestDeletePost:
    def test_delete_returns_none(self, post_client: PostApiClient) -> None:
        result = post_client.delete(post_id=1)
        assert result is None
