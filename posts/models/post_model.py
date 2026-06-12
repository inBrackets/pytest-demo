from typing import Any, Self

from models.base_model import AppBaseModel


class PostResponse(AppBaseModel):
    id: int
    user_id: int
    title: str
    body: str


class CreatePostRequest(AppBaseModel):
    user_id: int
    title: str
    body: str

    @classmethod
    def make(cls, **overrides: Any) -> Self:
        defaults: dict[str, Any] = {
            "user_id": 1,
            "title": "Test Title",
            "body": "Test body content.",
        }
        return cls(**{**defaults, **overrides})
