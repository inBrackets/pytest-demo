import logging
from abc import ABC, abstractmethod
from typing import Any, Generic, NoReturn, TypeVar

import allure
from pydantic import BaseModel, ValidationError
from playwright.sync_api import APIRequestContext, APIResponse

from core.config import Settings
from core.exceptions import ApiError
from models.base_model import AppBaseModel

T = TypeVar("T", bound=BaseModel)


def _raise_for_http_error(response: APIResponse, url: str) -> NoReturn:
    body = response.text()
    allure.attach(
        body,
        name=f"error-response-{response.status}",
        attachment_type=allure.attachment_type.TEXT,
    )
    raise ApiError(response.status, url, body)


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

    def _raise_for_status(self, response: APIResponse, url: str) -> None:
        self._logger.debug("← %d", response.status)
        if not response.ok:
            _raise_for_http_error(response, url)

    def _validated(self, data: Any) -> T:
        try:
            return self._response_model.model_validate(data)
        except ValidationError:
            allure.attach(
                str(data),
                name="schema-validation-failure",
                attachment_type=allure.attachment_type.TEXT,
            )
            raise

    def _get(self, resource_id: int | str, params: dict[str, Any] | None = None) -> T:
        url = f"{self.base_url}{self.endpoint}/{resource_id}"
        self._logger.debug("GET %s", url)
        response = self._context.get(url, params=params)
        self._raise_for_status(response, url)
        return self._validated(response.json())

    def _get_many(self, params: dict[str, Any] | None = None) -> list[T]:
        url = f"{self.base_url}{self.endpoint}"
        self._logger.debug("GET %s", url)
        response = self._context.get(url, params=params)
        self._raise_for_status(response, url)
        data = response.json()
        if not isinstance(data, list):
            raise ApiError(response.status, url, f"Expected list response, got {type(data).__name__}")
        return [self._validated(item) for item in data]

    def _post(self, payload: AppBaseModel) -> T:
        url = f"{self.base_url}{self.endpoint}"
        self._logger.debug("POST %s", url)
        response = self._context.post(url, data=payload.model_dump(by_alias=True))
        self._raise_for_status(response, url)
        return self._validated(response.json())

    def _put(self, resource_id: int | str, payload: AppBaseModel) -> T:
        url = f"{self.base_url}{self.endpoint}/{resource_id}"
        self._logger.debug("PUT %s", url)
        response = self._context.put(url, data=payload.model_dump(by_alias=True))
        self._raise_for_status(response, url)
        return self._validated(response.json())

    def _patch(self, resource_id: int | str, payload: AppBaseModel) -> T:
        url = f"{self.base_url}{self.endpoint}/{resource_id}"
        self._logger.debug("PATCH %s", url)
        response = self._context.patch(url, data=payload.model_dump(by_alias=True))
        self._raise_for_status(response, url)
        return self._validated(response.json())

    def _delete(self, resource_id: int | str) -> None:
        url = f"{self.base_url}{self.endpoint}/{resource_id}"
        self._logger.debug("DELETE %s", url)
        response = self._context.delete(url)
        self._raise_for_status(response, url)
