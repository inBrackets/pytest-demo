import pytest

from users.pages.login_page import LoginPage


@pytest.mark.ui
@pytest.mark.smoke
class TestLoginPage:
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
