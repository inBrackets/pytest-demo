import allure
import pytest
from playwright.sync_api import Page

from core.config import Settings
from core.state_validators import StateValidator
from users.pages.login_page import LoginPage


@allure.feature("Authentication")
@allure.story("Login")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.ui
@pytest.mark.smoke
class TestLoginPage:
    """TC 2 — Login User with Correct Credentials"""

    def test_page_loads(self, unauthenticated_page: Page, settings: Settings) -> None:
        LoginPage(page=unauthenticated_page, settings=settings).navigate()
        StateValidator.assert_url_contains(unauthenticated_page, "/login")

    def test_valid_credentials_redirect_away_from_login(
        self, unauthenticated_page: Page, settings: Settings, live_account: dict[str, str]
    ) -> None:
        LoginPage(page=unauthenticated_page, settings=settings).navigate().login(
            username=live_account["email"],
            password=live_account["password"],
        )
        StateValidator.assert_logged_in(unauthenticated_page)


@allure.feature("Authentication")
@allure.story("Login Validation")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.ui
class TestLoginWithInvalidCredentials:
    """TC 3 — Login User with Incorrect Email and Password"""

    def test_wrong_credentials_show_error_and_stay_on_login(
        self, unauthenticated_page: Page, settings: Settings
    ) -> None:
        login_page = LoginPage(page=unauthenticated_page, settings=settings).navigate()
        login_page.login(username="wrong@example.com", password="wrongpassword")
        assert "incorrect" in login_page.get_error_message().lower()
        StateValidator.assert_url_contains(unauthenticated_page, "/login")


@allure.feature("Authentication")
@allure.story("Logout")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ui
class TestLogout:
    """TC 4 — Logout User"""

    def test_logout_redirects_to_login(
        self, unauthenticated_page: Page, settings: Settings, live_account: dict[str, str]
    ) -> None:
        login_page = LoginPage(page=unauthenticated_page, settings=settings).navigate()
        login_page.login(
            username=live_account["email"],
            password=live_account["password"],
        )
        StateValidator.assert_logged_in(unauthenticated_page)
        unauthenticated_page.locator("a[href='/logout']").click()
        StateValidator.assert_logged_out(unauthenticated_page)
