import pytest

from contact.pages.contact_page import ContactPage


@pytest.mark.ui
class TestContactUsForm:
    """TC 6 — Contact Us Form"""

    def test_form_submission_shows_success(self, contact_page: ContactPage) -> None:
        contact_page.navigate()
        contact_page.submit(
            name="Pytest Tester",
            email="pytest@test.com",
            subject="Automated Test Submission",
            message="This is a test message submitted by the automated test suite.",
        )
        contact_page.is_success_visible()

    def test_success_allows_return_to_home(self, contact_page: ContactPage) -> None:
        contact_page.navigate()
        contact_page.submit(
            name="Pytest Tester",
            email="pytest@test.com",
            subject="Return Home Test",
            message="Testing return to home navigation.",
        )
        contact_page.is_success_visible()
        contact_page.go_home()
        assert contact_page._page.url.rstrip("/") == contact_page._settings.ui_base_url.rstrip("/")
