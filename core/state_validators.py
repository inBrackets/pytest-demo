import logging

import allure
from playwright.sync_api import Page, expect

_logger = logging.getLogger(__name__)


class StateValidator:
    """Reusable explicit state assertions for post-action verification.

    Call these after actions to make assertions self-documenting in Allure steps
    and logs, rather than scattering raw expect() calls across tests.
    """

    @staticmethod
    def assert_logged_in(page: Page) -> None:
        with allure.step("Assert authenticated session is active"):
            expect(page.locator("a[href='/logout']")).to_be_visible()
            _logger.info("Confirmed: user is logged in (logout link visible)")

    @staticmethod
    def assert_logged_out(page: Page) -> None:
        with allure.step("Assert no authenticated session"):
            expect(page.locator("a[href='/logout']")).not_to_be_visible()
            expect(page.locator("a[href='/login']")).to_be_visible()
            _logger.info("Confirmed: user is logged out (login link visible)")

    @staticmethod
    def assert_url_contains(page: Page, fragment: str) -> None:
        with allure.step(f"Assert URL contains '{fragment}'"):
            assert fragment in page.url, (
                f"Expected URL to contain '{fragment}', got: {page.url}"
            )
            _logger.info("Confirmed: URL contains '%s'", fragment)

    @staticmethod
    def assert_url_excludes(page: Page, fragment: str) -> None:
        with allure.step(f"Assert URL does not contain '{fragment}'"):
            assert fragment not in page.url, (
                f"Expected URL to not contain '{fragment}', got: {page.url}"
            )
            _logger.info("Confirmed: URL does not contain '%s'", fragment)

    @staticmethod
    def assert_text_visible(page: Page, text: str) -> None:
        with allure.step(f"Assert '{text}' is visible on page"):
            expect(page.get_by_text(text, exact=False)).to_be_visible()
            _logger.info("Confirmed: text '%s' is visible", text)
