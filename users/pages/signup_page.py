from typing import Self

import allure
from playwright.sync_api import Locator, expect

from core.base_page import BasePage


class SignupPage(BasePage):
    @property
    def url(self) -> str:
        return f"{self._settings.ui_base_url}/signup"

    # Locators
    @property
    def _account_info_heading(self) -> Locator:
        return self._page.locator("h2", has_text="Enter Account Information")

    @property
    def _title_mr(self) -> Locator:
        return self._page.locator("input#id_gender1")

    @property
    def _password_input(self) -> Locator:
        return self._page.locator("input[data-qa='password']")

    @property
    def _days_select(self) -> Locator:
        return self._page.locator("select[data-qa='days']")

    @property
    def _months_select(self) -> Locator:
        return self._page.locator("select[data-qa='months']")

    @property
    def _years_select(self) -> Locator:
        return self._page.locator("select[data-qa='years']")

    @property
    def _firstname_input(self) -> Locator:
        return self._page.locator("input[data-qa='first_name']")

    @property
    def _lastname_input(self) -> Locator:
        return self._page.locator("input[data-qa='last_name']")

    @property
    def _address_input(self) -> Locator:
        return self._page.locator("input[data-qa='address']")

    @property
    def _country_select(self) -> Locator:
        return self._page.locator("select[data-qa='country']")

    @property
    def _state_input(self) -> Locator:
        return self._page.locator("input[data-qa='state']")

    @property
    def _city_input(self) -> Locator:
        return self._page.locator("input[data-qa='city']")

    @property
    def _zipcode_input(self) -> Locator:
        return self._page.locator("input[data-qa='zipcode']")

    @property
    def _mobile_input(self) -> Locator:
        return self._page.locator("input[data-qa='mobile_number']")

    @property
    def _create_account_button(self) -> Locator:
        return self._page.locator("button[data-qa='create-account']")

    @property
    def _account_created_heading(self) -> Locator:
        return self._page.locator("h2[data-qa='account-created']")

    @property
    def _continue_button(self) -> Locator:
        return self._page.locator("a[data-qa='continue-button']")

    @property
    def _delete_account_link(self) -> Locator:
        return self._page.locator("a[href='/delete_account']")

    @property
    def _account_deleted_heading(self) -> Locator:
        return self._page.locator("h2[data-qa='account-deleted']")

    # Actions
    @allure.step("Verify signup page is loaded")
    def is_loaded(self) -> None:
        expect(self._account_info_heading).to_be_visible()

    @allure.step("Fill account information")
    def fill_account_info(
        self,
        password: str,
        day: str = "1",
        month: str = "January",
        year: str = "2000",
    ) -> Self:
        self._title_mr.check()
        self._password_input.fill(password)
        self._days_select.select_option(day)
        self._months_select.select_option(month)
        self._years_select.select_option(year)
        return self

    @allure.step("Fill address details")
    def fill_address(
        self,
        firstname: str = "Test",
        lastname: str = "User",
        address1: str = "123 Test Street",
        country: str = "United States",
        state: str = "California",
        city: str = "Los Angeles",
        zipcode: str = "90001",
        mobile: str = "1234567890",
    ) -> Self:
        self._firstname_input.fill(firstname)
        self._lastname_input.fill(lastname)
        self._address_input.fill(address1)
        self._country_select.select_option(country)
        self._state_input.fill(state)
        self._city_input.fill(city)
        self._zipcode_input.fill(zipcode)
        self._mobile_input.fill(mobile)
        return self

    @allure.step("Submit account creation form")
    def create_account(self) -> None:
        self._create_account_button.click()
        expect(self._account_created_heading).to_be_visible()

    @allure.step("Continue after account created")
    def continue_after_creation(self) -> None:
        self._continue_button.click()

    @allure.step("Click Delete Account in navigation")
    def delete_account_via_nav(self) -> None:
        self._delete_account_link.click()
        expect(self._account_deleted_heading).to_be_visible()
