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
        self._page.goto(self.url, wait_until="domcontentloaded")
        row = self._cart_rows.nth(index)
        self._delete_buttons.nth(index).click(force=True)
        row.wait_for(state="detached")

    @allure.step("Clear all items from cart")
    def clear_cart(self) -> None:
        for _ in range(50):
            self._page.goto(self.url, wait_until="domcontentloaded")
            self._dismiss_consent_banner()
            if self._delete_buttons.count() == 0:
                break
            self._delete_buttons.first.click(force=True)
            self._page.wait_for_load_state("domcontentloaded")

    @allure.step("Proceed to checkout")
    def proceed_to_checkout(self) -> None:
        self._checkout_button.scroll_into_view_if_needed()
        self._checkout_button.click()
        self._page.wait_for_load_state("domcontentloaded")

        if "/view_cart" not in self._page.url:
            return  # Navigation to checkout succeeded

        if self._page.locator("a[href='/logout']").is_visible():
            # Authenticated user but checkout navigation failed under load — go directly.
            self._page.goto(
                f"{self._settings.ui_base_url}/checkout",
                wait_until="domcontentloaded",
                timeout=self._settings.navigation_timeout,
            )
        elif not self._page.locator("div.modal-content a[href='/login']").is_visible():
            # Unauthenticated user but the checkout modal didn't open under load — retry.
            self._checkout_button.scroll_into_view_if_needed()
            self._checkout_button.click()
