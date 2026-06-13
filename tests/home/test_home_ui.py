import pytest

from playwright.sync_api import expect

from products.pages.home_page import HomePage


@pytest.mark.ui
class TestNavigateToTestCasesPage:
    """TC 7 — Verify Test Cases Page"""

    def test_test_cases_page_loads(self, home_page: HomePage) -> None:
        home_page.navigate()
        home_page.go_to_test_cases()
        assert "/test_cases" in home_page._page.url.split("#")[0]


@pytest.mark.ui
class TestScrollUpWithArrow:
    """TC 25 — Verify Scroll Up Using Arrow Button"""

    def test_scroll_up_arrow_returns_to_hero(self, home_page: HomePage) -> None:
        home_page.navigate()
        home_page.scroll_to_bottom()
        expect(home_page._page.locator("input#susbscribe_email")).to_be_visible()
        home_page.click_scroll_up_arrow()
        home_page._page.wait_for_load_state("networkidle")
        hero_text = home_page.get_hero_text()
        assert hero_text


@pytest.mark.ui
class TestScrollUpManually:
    """TC 26 — Verify Scroll Up Without Arrow Button"""

    def test_manual_scroll_up_returns_to_hero(self, home_page: HomePage) -> None:
        home_page.navigate()
        home_page.scroll_to_bottom()
        expect(home_page._page.locator("input#susbscribe_email")).to_be_visible()
        home_page.scroll_to_top()
        hero_text = home_page.get_hero_text()
        assert hero_text
