from pydantic import BaseModel, ConfigDict, Field


class AeBaseResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    response_code: int = Field(alias="responseCode")


class AeMessageResponse(AeBaseResponse):
    message: str
