from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field


class AeBaseResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    response_code: int = Field(alias="responseCode")


class AeMessageResponse(AeBaseResponse):
    message: str


class AeUserDetail(BaseModel):
    id: int
    name: str
    email: str
    title: str
    birth_day: str
    birth_month: str
    birth_year: str
    first_name: str
    last_name: str
    company: str
    address1: str
    address2: str
    country: str
    state: str
    city: str
    zipcode: str


class AeUserDetailResponse(AeBaseResponse):
    user: AeUserDetail


class AeCreateAccountRequest(BaseModel):
    name: str
    email: str
    password: str
    title: str = "Mr"
    birth_date: str = "1"
    birth_month: str = "1"
    birth_year: str = "2000"
    firstname: str = "Test"
    lastname: str = "User"
    company: str = "Test Co"
    address1: str = "123 Test Street"
    address2: str = ""
    country: str = "United States"
    zipcode: str = "90001"
    state: str = "California"
    city: str = "Los Angeles"
    mobile_number: str = "1234567890"

    @classmethod
    def make(cls, **overrides: Any) -> Self:
        defaults = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "Test1234!",
        }
        return cls(**{**defaults, **overrides})
