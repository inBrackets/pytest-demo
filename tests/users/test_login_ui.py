import pytest

from users.pages.login_page import LoginPage


@pytest.mark.ui
@pytest.mark.smoke
class TestLoginPage:
    """TC 2 — Login User with Correct Credentials"""

    def test_page_loads(self, unauthenticated_page, settings) -> None:
        LoginPage(page=unauthenticated_page, settings=settings).navigate()

    def test_valid_credentials_redirect_away_from_login(
        self, unauthenticated_page, settings
    ) -> None:
        LoginPage(page=unauthenticated_page, settings=settings).navigate().login(
            username=settings.ae_username,
            password=settings.ae_password.get_secret_value(),
        )
        assert "/login" not in unauthenticated_page.url


@pytest.mark.ui
class TestLoginWithInvalidCredentials:
    """TC 3 — Login User with Incorrect Email and Password"""

    def test_wrong_credentials_show_error(self, unauthenticated_page, settings) -> None:
        login_page = LoginPage(page=unauthenticated_page, settings=settings).navigate()
        login_page.login(username="wrong@example.com", password="wrongpassword")
        error = login_page.get_error_message()
        assert "incorrect" in error.lower()

    def test_page_stays_at_login_url(self, unauthenticated_page, settings) -> None:
        login_page = LoginPage(page=unauthenticated_page, settings=settings).navigate()
        login_page.login(username="wrong@example.com", password="wrongpassword")
        assert "/login" in unauthenticated_page.url


@pytest.mark.ui
class TestLogout:
    """TC 4 — Logout User"""

    def test_logout_redirects_to_login(self, unauthenticated_page, settings) -> None:
        login_page = LoginPage(page=unauthenticated_page, settings=settings).navigate()
        login_page.login(
            username=settings.ae_username,
            password=settings.ae_password.get_secret_value(),
        )
        assert "/login" not in unauthenticated_page.url
        unauthenticated_page.locator("a[href='/logout']").click()
        assert "/login" in unauthenticated_page.url
