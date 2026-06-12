import allure
from playwright.sync_api import expect

from core.base_page import BasePage


class ProductPage(BasePage):
    @property
    def url(self) -> str:
        return f"{self._settings.ui_base_url}/products"

    @allure.step("Verify product page is loaded")
    def is_loaded(self) -> None:
        expect(self._page.locator("h2", has_text="All Products")).to_be_visible()

    @allure.step("Get all product names")
    def get_product_names(self) -> list[str]:
        self._logger.debug("Collecting product names from listing")
        return self._page.locator(".productinfo p").all_inner_texts()
