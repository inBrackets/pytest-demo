import allure
from playwright.sync_api import Locator, expect

from core.base_page import BasePage


class CartPage(BasePage):
    @property
    def url(self) -> str:
        return f"{self._settings.ui_base_url}/view_cart"

    # Locators
    @property
    def _cart_rows(self) -> Locator:
        return self._page.locator("#cart_info_table tbody tr")

    @property
    def _product_name_links(self) -> Locator:
        return self._page.locator(".cart_description h4 a")

    @property
    def _quantity_buttons(self) -> Locator:
        return self._page.locator(".cart_quantity button")

    @property
    def _delete_buttons(self) -> Locator:
        return self._page.locator("a.cart_quantity_delete")

    @property
    def _subscribe_email(self) -> Locator:
        return self._page.locator("input#susbscribe_email")

    @property
    def _subscribe_button(self) -> Locator:
        return self._page.locator("button#subscribe")

    @property
    def _subscribe_success(self) -> Locator:
        return self._page.locator("div#success-subscribe")

    @property
    def _checkout_button(self) -> Locator:
        return self._page.locator("a.check_out")

    @property
    def _shopping_cart_breadcrumb(self) -> Locator:
        return self._page.locator("li:has-text('Shopping Cart')")

    # Actions
    @allure.step("Verify cart page is loaded")
    def is_loaded(self) -> None:
        expect(self._shopping_cart_breadcrumb).to_be_visible()

    @allure.step("Get number of products in cart")
    def get_product_count(self) -> int:
        return self._cart_rows.count()

    @allure.step("Get product names in cart")
    def get_product_names(self) -> list[str]:
        return self._product_name_links.all_inner_texts()

    @allure.step("Get product quantities in cart")
    def get_quantities(self) -> list[int]:
        texts = self._quantity_buttons.all_inner_texts()
        return [int(t.strip()) for t in texts]

    @allure.step("Remove product at index {index}")
    def remove_product(self, index: int = 0) -> None:
        self._delete_buttons.nth(index).click()
        self._page.wait_for_load_state("networkidle")

    @allure.step("Clear all items from cart")
    def clear_cart(self) -> None:
        while True:
            self._page.goto(self.url, wait_until="domcontentloaded")
            self._dismiss_consent_banner()
            if self._delete_buttons.count() == 0:
                break
            self._delete_buttons.first.click(force=True)
            self._page.wait_for_load_state("networkidle")

    @allure.step("Subscribe with email {email}")
    def subscribe(self, email: str) -> None:
        self._subscribe_email.fill(email)
        self._subscribe_button.click()
        expect(self._subscribe_success).to_be_visible()

    @allure.step("Proceed to checkout")
    def proceed_to_checkout(self) -> None:
        self._checkout_button.click()
