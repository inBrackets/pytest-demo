import logging
from abc import ABC
from typing import Any, cast

import allure
from playwright.sync_api import APIRequestContext, APIResponse

from core.config import Settings
from core.exceptions import ApiError


class AeBaseClient(ABC):
    def __init__(self, context: APIRequestContext, settings: Settings) -> None:
        self._context = context
        self._settings = settings
        self._logger = logging.getLogger(self.__class__.__module__)

    @property
    def _base_url(self) -> str:
        return self._settings.ae_api_base_url

    def _raise_for_status(self, response: APIResponse, url: str) -> None:
        self._logger.debug("← %d", response.status)
        if not response.ok:
            body = response.text()
            allure.attach(
                body,
                name=f"error-response-{response.status}",
                attachment_type=allure.attachment_type.TEXT,
            )
            raise ApiError(response.status, url, body)

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self._base_url}{path}"
        self._logger.debug("GET %s", url)
        response = self._context.get(url, params=params)
        self._raise_for_status(response, url)
        return cast(dict[str, Any], response.json())

    def _post(self, path: str, form: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self._base_url}{path}"
        self._logger.debug("POST %s", url)
        response = self._context.post(url, form=form or {})
        self._raise_for_status(response, url)
        return cast(dict[str, Any], response.json())

    def _put(self, path: str, form: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self._base_url}{path}"
        self._logger.debug("PUT %s", url)
        response = self._context.put(url, form=form or {})
        self._raise_for_status(response, url)
        return cast(dict[str, Any], response.json())

    def _delete(self, path: str, form: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self._base_url}{path}"
        self._logger.debug("DELETE %s", url)
        response = self._context.delete(url, form=form or {})
        self._raise_for_status(response, url)
        return cast(dict[str, Any], response.json())
