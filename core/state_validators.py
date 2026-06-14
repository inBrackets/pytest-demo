import logging
from typing import Any, Callable

import allure
import pytest
from playwright.sync_api import Page, expect

from core.exceptions import ApiError

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
        StateValidator._check_url(page, fragment, present=True)

    @staticmethod
    def assert_url_excludes(page: Page, fragment: str) -> None:
        StateValidator._check_url(page, fragment, present=False)

    @staticmethod
    def assert_text_visible(page: Page, text: str) -> None:
        with allure.step(f"Assert '{text}' is visible on page"):
            expect(page.get_by_text(text, exact=False)).to_be_visible()
            _logger.info("Confirmed: text '%s' is visible", text)

    @staticmethod
    def assert_resource_exists(get_fn: Callable[[], Any]) -> None:
        # Calls get_fn(); asserts it returns non-None without raising.
        with allure.step("Assert resource exists"):
            result = get_fn()
            assert result is not None
            _logger.info("Confirmed: resource exists")

    @staticmethod
    def assert_resource_deleted(get_fn: Callable[[], Any]) -> None:
        # Calls get_fn(); asserts it raises ApiError(404).
        with allure.step("Assert resource is deleted (expects 404)"):
            with pytest.raises(ApiError) as exc_info:
                get_fn()
            assert exc_info.value.status_code == 404
            _logger.info("Confirmed: resource is deleted (404 returned)")

    @staticmethod
    def _check_url(page: Page, fragment: str, *, present: bool) -> None:
        verb = "contains" if present else "does not contain"
        with allure.step(f"Assert URL {verb} '{fragment}'"):
            ok = (fragment in page.url) if present else (fragment not in page.url)
            assert ok, f"Expected URL to {verb} '{fragment}', got: {page.url}"
            _logger.info("Confirmed: URL %s '%s'", verb, fragment)
