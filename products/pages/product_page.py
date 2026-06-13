import allure
from playwright.sync_api import Locator, expect

from core.base_page import BasePage


class ProductPage(BasePage):
    @property
    def url(self) -> str:
        return f"{self._settings.ui_base_url}/products"

    # Locators
    @property
    def _all_products_heading(self) -> Locator:
        return self._page.locator("h2", has_text="All Products")

    @property
    def _product_names(self) -> Locator:
        return self._page.locator(".productinfo p")

    @property
    def _search_input(self) -> Locator:
        return self._page.locator("#search_product")

    @property
    def _search_button(self) -> Locator:
        return self._page.locator("#submit_search")

    @property
    def _view_product_links(self) -> Locator:
        return self._page.locator("a:has-text('View Product')")

    @property
    def _product_cards(self) -> Locator:
        return self._page.locator(".productinfo")

    @property
    def _cart_modal(self) -> Locator:
        return self._page.locator("div.modal-content")

    @property
    def _continue_shopping_button(self) -> Locator:
        return self._page.locator("button.close-modal")

    @property
    def _cart_modal_link(self) -> Locator:
        return self._page.locator("div.modal-content a[href='/view_cart']")

    # Actions
    @allure.step("Verify product page is loaded")
    def is_loaded(self) -> None:
        expect(self._all_products_heading).to_be_visible()

    @allure.step("Get product names")
    def get_product_names(self) -> list[str]:
        self._logger.debug("Collecting product names from listing")
        return self._product_names.all_inner_texts()

    @allure.step("Search for '{product_name}'")
    def search(self, product_name: str) -> None:
        self._logger.debug("Searching for %s", product_name)
        self._search_input.fill(product_name)
        self._search_button.click()
        self._page.wait_for_load_state("networkidle")

    @allure.step("Click View Product at index {index}")
    def click_view_product(self, index: int = 0) -> None:
        self._view_product_links.nth(index).click()

    @allure.step("Add product at index {index} to cart")
    def add_to_cart(self, index: int = 0) -> None:
        product = self._product_cards.nth(index)
        product.hover()
        product.locator("a:has-text('Add to cart')").click()
        self._cart_modal.wait_for(state="visible")

    @allure.step("Continue shopping from modal")
    def continue_shopping(self) -> None:
        self._continue_shopping_button.click()

    @allure.step("View cart from modal")
    def view_cart_from_modal(self) -> None:
        self._cart_modal_link.click()

    @allure.step("Click brand '{brand_name}' in sidebar")
    def click_brand(self, brand_name: str) -> None:
        self._page.locator(".brands-name a", has_text=brand_name).click()
        self._page.wait_for_load_state("domcontentloaded")

    @allure.step("Click category '{category}' then subcategory '{subcategory}'")
    def select_category(self, category: str, subcategory: str) -> None:
        self._page.locator(f"#accordian a[href='#{category}']").click()
        sub = self._page.locator(f"#{category} a", has_text=subcategory)
        sub.wait_for(state="visible")
        sub.click()
        self._page.wait_for_load_state("domcontentloaded")
