from typing import Self

import allure
from playwright.sync_api import Locator, expect

from core.base_page import BasePage


class CheckoutPage(BasePage):
    @property
    def url(self) -> str:
        return f"{self._settings.ui_base_url}/checkout"

    # Locators
    @property
    def _delivery_address_section(self) -> Locator:
        return self._page.locator("#address_delivery")

    @property
    def _delivery_address_lines(self) -> Locator:
        return self._page.locator("#address_delivery li")

    @property
    def _billing_address_lines(self) -> Locator:
        return self._page.locator("#address_invoice li")

    @property
    def _order_comment(self) -> Locator:
        return self._page.locator("textarea.form-control")

    @property
    def _place_order_button(self) -> Locator:
        return self._page.locator("a:has-text('Place Order')")

    # Actions
    @allure.step("Verify checkout page is loaded")
    def is_loaded(self) -> None:
        expect(self._delivery_address_section).to_be_visible()

    @allure.step("Get delivery address lines")
    def get_delivery_address(self) -> list[str]:
        return self._delivery_address_lines.all_inner_texts()

    @allure.step("Get billing address lines")
    def get_billing_address(self) -> list[str]:
        return self._billing_address_lines.all_inner_texts()

    @allure.step("Enter order comment")
    def add_comment(self, comment: str) -> Self:
        self._order_comment.fill(comment)
        return self

    @allure.step("Click Place Order")
    def place_order(self) -> None:
        self._place_order_button.click()
