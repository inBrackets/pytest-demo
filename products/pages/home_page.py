import allure
from playwright.sync_api import expect

from core.base_page import BasePage


class HomePage(BasePage):
    @property
    def url(self) -> str:
        return self._settings.ui_base_url

    @allure.step("Verify home page is loaded")
    def is_loaded(self) -> None:
        expect(self._page.locator("h2", has_text="Features Items")).to_be_visible()

    @allure.step("Search for '{product_name}'")
    def search(self, product_name: str) -> None:
        self._logger.debug("Searching for %s", product_name)
        self._page.locator("#search_product").fill(product_name)
        self._page.locator("#submit_search").click()
