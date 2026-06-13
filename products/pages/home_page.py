import allure
from playwright.sync_api import expect

from core.base_page import BasePage


class HomePage(BasePage):
    @property
    def url(self) -> str:
        return self._settings.ui_base_url

    # Locators
    @property
    def _features_heading(self):
        return self._page.locator("h2", has_text="Features Items")

    @property
    def _nav_products(self):
        return self._page.locator("a[href='/products']").first

    @property
    def _nav_cart(self):
        return self._page.locator("a[href='/view_cart']").first

    @property
    def _nav_test_cases(self):
        return self._page.locator("a[href='/test_cases']").first

    @property
    def _nav_contact_us(self):
        return self._page.locator("a[href='/contact_us']").first

    @property
    def _subscribe_email(self):
        return self._page.locator("input#susbscribe_email")

    @property
    def _subscribe_button(self):
        return self._page.locator("button#subscribe")

    @property
    def _subscribe_success(self):
        return self._page.locator("div#success-subscribe")

    @property
    def _scroll_up_arrow(self):
        return self._page.locator("a#scrollUp")

    @property
    def _hero_heading(self):
        return self._page.locator(".item.active h2").first

    @property
    def _recommended_add_to_cart(self):
        return self._page.locator("#recommended-item-carousel .add-to-cart")

    @property
    def _cart_modal_link(self):
        return self._page.locator("div.modal-content a[href='/view_cart']")

    # Actions
    @allure.step("Verify home page is loaded")
    def is_loaded(self) -> None:
        expect(self._features_heading).to_be_visible()

    @allure.step("Click 'Products' in navigation")
    def go_to_products(self) -> None:
        self._nav_products.click()

    @allure.step("Click 'Cart' in navigation")
    def go_to_cart(self) -> None:
        self._nav_cart.click()

    @allure.step("Click 'Test Cases' in navigation")
    def go_to_test_cases(self) -> None:
        self._nav_test_cases.click()

    @allure.step("Click 'Contact us' in navigation")
    def go_to_contact_us(self) -> None:
        self._nav_contact_us.click()

    @allure.step("Subscribe with email {email}")
    def subscribe(self, email: str) -> None:
        self._subscribe_email.fill(email)
        self._subscribe_button.click()
        expect(self._subscribe_success).to_be_visible()

    @allure.step("Scroll to bottom of page")
    def scroll_to_bottom(self) -> None:
        self._page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        self._page.wait_for_load_state("networkidle")

    @allure.step("Click scroll-up arrow button")
    def click_scroll_up_arrow(self) -> None:
        self._scroll_up_arrow.click()

    @allure.step("Scroll to top of page")
    def scroll_to_top(self) -> None:
        self._page.evaluate("window.scrollTo(0, 0)")

    @allure.step("Get hero banner text")
    def get_hero_text(self) -> str:
        return self._hero_heading.inner_text()

    @allure.step("Add recommended item at index {index} to cart")
    def add_recommended_to_cart(self, index: int = 0) -> None:
        self._recommended_add_to_cart.nth(index).click()
        self._page.locator("div.modal-content").wait_for(state="visible")

    @allure.step("View cart from modal")
    def view_cart_from_modal(self) -> None:
        self._cart_modal_link.click()
