import allure
from playwright.sync_api import expect

from core.base_page import BasePage


class LoginPage(BasePage):
    @property
    def url(self) -> str:
        return f"{self._settings.ui_base_url}/login"

    @allure.step("Verify login page is loaded")
    def is_loaded(self) -> None:
        expect(self._page.locator("input[name='email']")).to_be_visible()

    @allure.step("Login as {username}")
    def login(self, username: str, password: str) -> None:
        self._logger.debug("Logging in as %s", username)
        self._page.locator("input[name='email']").fill(username)
        self._page.locator("input[name='password']").fill(password)
        self._page.locator("button[data-qa='login-button']").click()
