import logging
from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from playwright.sync_api import APIRequestContext

from core.config import Settings
from core.exceptions import ApiError
from models.base_model import AppBaseModel

T = TypeVar("T", bound=BaseModel)


class BaseApiClient(ABC, Generic[T]):
    _response_model: type[T]

    def __init__(self, context: APIRequestContext, settings: Settings) -> None:
        self._context = context
        self._settings = settings
        self._logger = logging.getLogger(self.__class__.__module__)

    @property
    @abstractmethod
    def base_url(self) -> str: ...

    @property
    @abstractmethod
    def endpoint(self) -> str: ...

    def _get(self, resource_id: int | str, params: dict[str, Any] | None = None) -> T:
        url = f"{self.base_url}{self.endpoint}/{resource_id}"
        self._logger.debug("GET %s", url)
        response = self._context.get(url, params=params)
        self._logger.debug("← %d", response.status)
        if not response.ok:
            raise ApiError(response.status, url, response.text())
        return self._response_model.model_validate(response.json())

    def _get_many(self, params: dict[str, Any] | None = None) -> list[T]:
        url = f"{self.base_url}{self.endpoint}"
        self._logger.debug("GET %s", url)
        response = self._context.get(url, params=params)
        self._logger.debug("← %d", response.status)
        if not response.ok:
            raise ApiError(response.status, url, response.text())
        data = response.json()
        if not isinstance(data, list):
            raise ApiError(response.status, url, f"Expected list response, got {type(data).__name__}")
        return [self._response_model.model_validate(item) for item in data]

    def _post(self, payload: AppBaseModel) -> T:
        url = f"{self.base_url}{self.endpoint}"
        self._logger.debug("POST %s", url)
        response = self._context.post(url, data=payload.model_dump(by_alias=True))
        self._logger.debug("← %d", response.status)
        if not response.ok:
            raise ApiError(response.status, url, response.text())
        return self._response_model.model_validate(response.json())

    def _put(self, resource_id: int | str, payload: AppBaseModel) -> T:
        url = f"{self.base_url}{self.endpoint}/{resource_id}"
        self._logger.debug("PUT %s", url)
        response = self._context.put(url, data=payload.model_dump(by_alias=True))
        self._logger.debug("← %d", response.status)
        if not response.ok:
            raise ApiError(response.status, url, response.text())
        return self._response_model.model_validate(response.json())

    def _patch(self, resource_id: int | str, payload: AppBaseModel) -> T:
        url = f"{self.base_url}{self.endpoint}/{resource_id}"
        self._logger.debug("PATCH %s", url)
        response = self._context.patch(url, data=payload.model_dump(by_alias=True))
        self._logger.debug("← %d", response.status)
        if not response.ok:
            raise ApiError(response.status, url, response.text())
        return self._response_model.model_validate(response.json())

    def _delete(self, resource_id: int | str) -> None:
        url = f"{self.base_url}{self.endpoint}/{resource_id}"
        self._logger.debug("DELETE %s", url)
        response = self._context.delete(url)
        self._logger.debug("← %d", response.status)
        if not response.ok:
            raise ApiError(response.status, url, response.text())
