from pydantic import BaseModel, ConfigDict, Field


class AeBaseResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    response_code: int = Field(alias="responseCode")


class AeUserType(BaseModel):
    usertype: str


class AeCategory(BaseModel):
    usertype: AeUserType
    category: str


class AeProduct(BaseModel):
    id: int
    name: str
    price: str
    brand: str
    category: AeCategory


class AeProductsResponse(AeBaseResponse):
    products: list[AeProduct]


class AeBrand(BaseModel):
    id: int
    brand: str


class AeBrandsResponse(AeBaseResponse):
    brands: list[AeBrand]


class AeMessageResponse(AeBaseResponse):
    message: str
