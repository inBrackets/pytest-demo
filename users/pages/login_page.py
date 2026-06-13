import allure
from playwright.sync_api import expect

from core.base_page import BasePage


class LoginPage(BasePage):
    @property
    def url(self) -> str:
        return f"{self._settings.ui_base_url}/login"

    # Locators
    @property
    def _login_email(self):
        return self._page.locator("input[data-qa='login-email']")

    @property
    def _login_password(self):
        return self._page.locator("input[data-qa='login-password']")

    @property
    def _login_button(self):
        return self._page.locator("button[data-qa='login-button']")

    @property
    def _login_error(self):
        return self._page.locator("p:has-text('Your email or password is incorrect!')")

    @property
    def _signup_name(self):
        return self._page.locator("input[data-qa='signup-name']")

    @property
    def _signup_email(self):
        return self._page.locator("input[data-qa='signup-email']")

    @property
    def _signup_button(self):
        return self._page.locator("button[data-qa='signup-button']")

    @property
    def _signup_error(self):
        return self._page.locator("p:has-text('Email Address already exist!')")

    # Actions
    @allure.step("Verify login page is loaded")
    def is_loaded(self) -> None:
        expect(self._login_email).to_be_visible()

    @allure.step("Login as {username}")
    def login(self, username: str, password: str) -> None:
        self._logger.debug("Logging in as %s", username)
        self._login_email.fill(username)
        self._login_password.fill(password)
        self._dismiss_consent_banner()
        self._login_button.click()

    @allure.step("Get login error message")
    def get_error_message(self) -> str:
        return self._login_error.inner_text()

    @allure.step("Start signup for {name}")
    def start_signup(self, name: str, email: str) -> None:
        self._logger.debug("Starting signup for %s", email)
        self._signup_name.fill(name)
        self._signup_email.fill(email)
        self._signup_button.click()

    @allure.step("Get signup error message")
    def get_signup_error(self) -> str:
        return self._signup_error.inner_text()
