import logging
from abc import ABC, abstractmethod
from typing import Self

import allure
from playwright.sync_api import Page, expect

from core.config import Settings


class BasePage(ABC):
    def __init__(self, page: Page, settings: Settings) -> None:
        self._page = page
        self._settings = settings
        self._logger = logging.getLogger(self.__class__.__module__)

    @property
    @abstractmethod
    def url(self) -> str: ...

    @abstractmethod
    def is_loaded(self) -> None: ...

    @allure.step("Navigate to {self.url}")
    def navigate(self) -> Self:
        self._logger.debug("Navigating to %s", self.url)
        self._page.goto(self.url)
        self.is_loaded()
        return self
