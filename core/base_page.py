import logging
from abc import ABC, abstractmethod
from typing import Self

import allure
from playwright.sync_api import Locator, Page, TimeoutError as PlaywrightTimeoutError, expect

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

    @property
    def current_url(self) -> str:
        return self._page.url

    def navigate(self) -> Self:
        with allure.step(f"Navigate to {self.url}"):
            self._logger.debug("Navigating to %s", self.url)
            self._page.goto(self.url, wait_until="domcontentloaded", timeout=self._settings.navigation_timeout)
            self._dismiss_consent_banner()
            self.is_loaded()
            return self

    def _click_and_navigate(self, locator: Locator, target_url: str) -> None:
        locator.click()
        self._page.wait_for_load_state("domcontentloaded")
        if self._page.url.split("?")[0].rstrip("/") != target_url.rstrip("/"):
            self._page.goto(target_url, wait_until="domcontentloaded", timeout=self._settings.navigation_timeout)
        self._dismiss_consent_banner()

    def _dismiss_consent_banner(self) -> None:
        try:
            self._page.locator(".fc-cta-consent").first.click(timeout=self._settings.consent_banner_timeout)
            self._page.locator(".fc-consent-root").wait_for(state="hidden", timeout=self._settings.consent_banner_timeout)
            self._logger.debug("Dismissed cookie consent banner")
        except PlaywrightTimeoutError:
            pass

    # Subscribe widget — present in the footer on all pages
    @property
    def _subscribe_email(self) -> Locator:
        return self._page.locator("input#susbscribe_email")

    @property
    def _subscribe_button(self) -> Locator:
        return self._page.locator("button#subscribe")

    @property
    def _subscribe_success(self) -> Locator:
        return self._page.locator("div#success-subscribe")

    # Add-to-cart confirmation modal — shown on any page after adding a product
    @property
    def _cart_modal(self) -> Locator:
        return self._page.locator("div.modal-content")

    @property
    def _cart_modal_link(self) -> Locator:
        return self._page.locator("div.modal-content a[href='/view_cart']")

    @allure.step("Subscribe with email {email}")
    def subscribe(self, email: str) -> None:
        self._subscribe_email.fill(email)
        self._subscribe_button.click()
        expect(self._subscribe_success).to_be_visible()

    @allure.step("View cart from modal")
    def view_cart_from_modal(self) -> None:
        self._cart_modal_link.click()
