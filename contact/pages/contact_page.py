import allure
from playwright.sync_api import Locator, expect

from core.base_page import BasePage


class ContactPage(BasePage):
    @property
    def url(self) -> str:
        return f"{self._settings.ui_base_url}/contact_us"

    # Locators
    @property
    def _get_in_touch_heading(self) -> Locator:
        return self._page.locator("h2", has_text="Get In Touch")

    @property
    def _name_input(self) -> Locator:
        return self._page.locator("input[data-qa='name']")

    @property
    def _email_input(self) -> Locator:
        return self._page.locator("input[data-qa='email']")

    @property
    def _subject_input(self) -> Locator:
        return self._page.locator("input[data-qa='subject']")

    @property
    def _message_textarea(self) -> Locator:
        return self._page.locator("textarea[data-qa='message']")

    @property
    def _submit_button(self) -> Locator:
        return self._page.locator("input[data-qa='submit-button']")

    @property
    def _success_status(self) -> Locator:
        return self._page.locator(".status.alert-success")

    @property
    def _home_link(self) -> Locator:
        return self._page.locator("a:has-text('Home')").first

    # Actions
    @allure.step("Verify contact page is loaded")
    def is_loaded(self) -> None:
        expect(self._get_in_touch_heading).to_be_visible()

    @allure.step("Submit contact form")
    def submit(self, name: str, email: str, subject: str, message: str) -> None:
        self._name_input.fill(name)
        self._email_input.fill(email)
        self._subject_input.fill(subject)
        self._message_textarea.fill(message)
        self._page.once("dialog", lambda d: d.accept())
        self._submit_button.click()

    @allure.step("Verify success message is visible")
    def is_success_visible(self) -> None:
        expect(self._success_status).to_be_visible()

    @allure.step("Return to home page")
    def go_home(self) -> None:
        self._click_and_navigate(self._home_link, self._settings.ui_base_url)
