from typing import Any, Self

from models.base_model import AppBaseModel


class UserResponse(AppBaseModel):
    id: int
    name: str
    username: str
    email: str


class CreateUserRequest(AppBaseModel):
    name: str
    username: str
    email: str

    @classmethod
    def make(cls, **overrides: Any) -> Self:
        defaults: dict[str, Any] = {
            "name": "Test User",
            "username": "testuser",
            "email": "test@example.com",
        }
        return cls(**{**defaults, **overrides})
