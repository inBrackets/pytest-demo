import allure
import pytest
from playwright.sync_api import Page

from core.config import Settings
from core.state_validators import StateValidator
from users.pages.login_page import LoginPage
from users.pages.signup_page import SignupPage


@allure.feature("Authentication")
@allure.story("Registration")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ui
@pytest.mark.smoke
class TestRegisterUser:
    """TC 1 — Register User"""

    def test_new_user_can_register(
        self,
        unauthenticated_page: Page,
        settings: Settings,
        disposable_credentials: dict[str, str],
    ) -> None:
        login_page = LoginPage(page=unauthenticated_page, settings=settings).navigate()
        login_page.start_signup(
            name=disposable_credentials["name"],
            email=disposable_credentials["email"],
        )
        signup = SignupPage(page=unauthenticated_page, settings=settings)
        signup.is_loaded()
        signup.fill_account_info(password=disposable_credentials["password"])
        signup.fill_address()
        signup.create_account()

    def test_account_created_page_shows_success(
        self,
        unauthenticated_page: Page,
        settings: Settings,
        disposable_credentials: dict[str, str],
    ) -> None:
        login_page = LoginPage(page=unauthenticated_page, settings=settings).navigate()
        login_page.start_signup(
            name=disposable_credentials["name"],
            email=disposable_credentials["email"],
        )
        signup = SignupPage(page=unauthenticated_page, settings=settings)
        signup.is_loaded()
        signup.fill_account_info(password=disposable_credentials["password"])
        signup.fill_address()
        signup.create_account()
        StateValidator.assert_url_contains(unauthenticated_page, "account_created")


@allure.feature("Authentication")
@allure.story("Registration Validation")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.ui
class TestRegisterWithExistingEmail:
    """TC 5 — Register User with Existing Email"""

    def test_existing_email_shows_error(
        self,
        unauthenticated_page: Page,
        settings: Settings,
        live_account: dict[str, str],
    ) -> None:
        login_page = LoginPage(page=unauthenticated_page, settings=settings).navigate()
        login_page.start_signup(name="Any Name", email=live_account["email"])
        error = login_page.get_signup_error()
        assert "already exist" in error.lower()
