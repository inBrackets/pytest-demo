import allure
from playwright.sync_api import Locator, expect

from core.base_page import BasePage


class PaymentPage(BasePage):
    @property
    def url(self) -> str:
        return f"{self._settings.ui_base_url}/payment"

    # Locators
    @property
    def _name_on_card(self) -> Locator:
        return self._page.locator("input[data-qa='name-on-card']")

    @property
    def _card_number(self) -> Locator:
        return self._page.locator("input[data-qa='card-number']")

    @property
    def _cvc(self) -> Locator:
        return self._page.locator("input[data-qa='cvc']")

    @property
    def _expiry_month(self) -> Locator:
        return self._page.locator("input[data-qa='expiry-month']")

    @property
    def _expiry_year(self) -> Locator:
        return self._page.locator("input[data-qa='expiry-year']")

    @property
    def _pay_button(self) -> Locator:
        return self._page.locator("button[data-qa='pay-button']")

    @property
    def _success_message(self) -> Locator:
        return self._page.locator("p:has-text('Congratulations'), #success_message")

    @property
    def _download_invoice_button(self) -> Locator:
        return self._page.locator("a.btn-default:has-text('Download Invoice')")

    # Actions
    @allure.step("Verify payment page is loaded")
    def is_loaded(self) -> None:
        expect(self._name_on_card).to_be_visible()

    @allure.step("Fill payment details")
    def fill_payment(
        self,
        name_on_card: str = "Test User",
        card_number: str = "4111111111111111",
        cvc: str = "123",
        exp_month: str = "01",
        exp_year: str = "2027",
    ) -> None:
        self._name_on_card.fill(name_on_card)
        self._card_number.fill(card_number)
        self._cvc.fill(cvc)
        self._expiry_month.fill(exp_month)
        self._expiry_year.fill(exp_year)

    @allure.step("Confirm payment")
    def confirm_payment(self) -> None:
        self._pay_button.click()
        expect(self._success_message).to_be_visible(timeout=15_000)

    @allure.step("Download invoice")
    def download_invoice(self) -> str:
        with self._page.expect_download() as dl_info:
            self._download_invoice_button.click()
        return dl_info.value.suggested_filename
