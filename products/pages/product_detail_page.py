from typing import Self

import allure
from playwright.sync_api import Locator, expect

from core.base_page import BasePage


class ProductDetailPage(BasePage):
    @property
    def url(self) -> str:
        return f"{self._settings.ui_base_url}/product_details"

    # Locators
    @property
    def _product_info(self) -> Locator:
        return self._page.locator(".product-information")

    @property
    def _product_name(self) -> Locator:
        return self._page.locator(".product-information h2")

    @property
    def _product_price(self) -> Locator:
        return self._page.locator(".product-information span span").first

    @property
    def _product_category(self) -> Locator:
        return self._page.locator(".product-information p", has_text="Category")

    @property
    def _product_availability(self) -> Locator:
        return self._page.locator(".product-information p", has_text="Availability")

    @property
    def _product_brand(self) -> Locator:
        return self._page.locator(".product-information p", has_text="Brand")

    @property
    def _quantity_input(self) -> Locator:
        return self._page.locator("input#quantity")

    @property
    def _add_to_cart_button(self) -> Locator:
        return self._page.locator("button.cart")

    @property
    def _continue_shopping_button(self) -> Locator:
        return self._page.locator("button.close-modal")

    @property
    def _review_name(self) -> Locator:
        return self._page.locator("input#name")

    @property
    def _review_email(self) -> Locator:
        return self._page.locator("input#email")

    @property
    def _review_text(self) -> Locator:
        return self._page.locator("textarea#review")

    @property
    def _review_submit_button(self) -> Locator:
        return self._page.locator("button#button-review")

    @property
    def _review_success(self) -> Locator:
        return self._page.locator("div.alert-success").first

    # Actions
    @allure.step("Verify product detail page is loaded")
    def is_loaded(self) -> None:
        expect(self._product_info).to_be_visible()

    @allure.step("Navigate to product details for product {product_id}")
    def navigate_to(self, product_id: int) -> Self:
        self._page.goto(
            f"{self._settings.ui_base_url}/product_details/{product_id}",
            wait_until="domcontentloaded",
        )
        self._dismiss_consent_banner()
        self.is_loaded()
        return self

    @allure.step("Get product name")
    def get_name(self) -> str:
        return self._product_name.inner_text()

    @allure.step("Get product price")
    def get_price(self) -> str:
        return self._product_price.inner_text()

    @allure.step("Get product category")
    def get_category(self) -> str:
        return self._product_category.inner_text()

    @allure.step("Get product availability")
    def get_availability(self) -> str:
        return self._product_availability.inner_text()

    @allure.step("Get product brand")
    def get_brand(self) -> str:
        return self._product_brand.inner_text()

    @allure.step("Set quantity to {qty}")
    def set_quantity(self, qty: int) -> Self:
        self._quantity_input.fill(str(qty))
        return self

    @allure.step("Add to cart")
    def add_to_cart(self) -> None:
        self._add_to_cart_button.click()
        self._cart_modal.wait_for(state="visible")

    @allure.step("Continue shopping from modal")
    def continue_shopping(self) -> None:
        self._continue_shopping_button.click()

    @allure.step("View cart from modal")
    def view_cart(self) -> None:
        self._cart_modal_link.click()

    @allure.step("Submit review")
    def submit_review(self, name: str, email: str, review: str) -> None:
        self._review_name.fill(name)
        self._review_email.fill(email)
        self._review_text.fill(review)
        self._review_submit_button.click()
        expect(self._review_success).to_be_visible()
