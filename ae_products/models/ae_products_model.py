from pydantic import BaseModel

from core.ae_models import AeBaseResponse


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

