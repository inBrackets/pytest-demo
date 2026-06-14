import pytest
from playwright.sync_api import Page

from checkout.pages.checkout_page import CheckoutPage
from checkout.pages.payment_page import PaymentPage
from core.config import Settings
from products.pages.cart_page import CartPage
from products.pages.product_page import ProductPage
from users.pages.login_page import LoginPage
from users.pages.signup_page import SignupPage

from tests.checkout.helpers import add_product_and_checkout


@pytest.mark.ui
class TestPlaceOrderRegisterBeforeCheckout:
    """TC 15 — Place Order: Register Before Checkout"""

    def test_order_placed_successfully(
        self,
        registered_page: Page,
        settings: Settings,
    ) -> None:
        add_product_and_checkout(registered_page, settings)
        checkout = CheckoutPage(page=registered_page, settings=settings)
        checkout.is_loaded()
        checkout.add_comment("Automated test order")
        checkout.place_order()
        payment = PaymentPage(page=registered_page, settings=settings)
        payment.is_loaded()
        payment.fill_payment()
        payment.confirm_payment()


@pytest.mark.ui
class TestPlaceOrderLoginBeforeCheckout:
    """TC 16 — Place Order: Login Before Checkout"""

    def test_order_placed_after_login(
        self,
        registered_page: Page,
        settings: Settings,
    ) -> None:
        add_product_and_checkout(registered_page, settings)
        checkout = CheckoutPage(page=registered_page, settings=settings)
        checkout.is_loaded()
        checkout.add_comment("Login before checkout test")
        checkout.place_order()
        payment = PaymentPage(page=registered_page, settings=settings)
        payment.is_loaded()
        payment.fill_payment()
        payment.confirm_payment()


@pytest.mark.ui
class TestPlaceOrderRegisterDuringCheckout:
    """TC 14 — Place Order: Register During Checkout"""

    def test_order_placed_after_registering_at_checkout(
        self,
        unauthenticated_page: Page,
        settings: Settings,
        disposable_credentials: dict[str, str],
    ) -> None:
        product_pg = ProductPage(page=unauthenticated_page, settings=settings)
        product_pg.navigate()
        product_pg.add_to_cart(index=0)
        product_pg.view_cart_from_modal()

        cart = CartPage(page=unauthenticated_page, settings=settings)
        cart.is_loaded()
        cart.proceed_to_checkout()

        unauthenticated_page.locator("a:has-text('Register / Login')").click()

        login_pg = LoginPage(page=unauthenticated_page, settings=settings)
        login_pg.start_signup(
            name=disposable_credentials["name"],
            email=disposable_credentials["email"],
        )
        signup = SignupPage(page=unauthenticated_page, settings=settings)
        signup.is_loaded()
        signup.fill_account_info(password=disposable_credentials["password"])
        signup.fill_address()
        signup.create_account()
        signup.continue_after_creation()

        unauthenticated_page.locator("a[href='/view_cart']").first.click()
        cart = CartPage(page=unauthenticated_page, settings=settings)
        cart.is_loaded()
        cart.proceed_to_checkout()

        checkout = CheckoutPage(page=unauthenticated_page, settings=settings)
        checkout.is_loaded()
        checkout.add_comment("Register during checkout test")
        checkout.place_order()
        payment = PaymentPage(page=unauthenticated_page, settings=settings)
        payment.is_loaded()
        payment.fill_payment()
        payment.confirm_payment()


@pytest.mark.ui
class TestVerifyAddressAtCheckout:
    """TC 23 — Verify Address Details in Checkout Page"""

    def test_delivery_address_is_not_empty(
        self,
        registered_page: Page,
        settings: Settings,
    ) -> None:
        add_product_and_checkout(registered_page, settings)
        checkout = CheckoutPage(page=registered_page, settings=settings)
        checkout.is_loaded()
        address_lines = checkout.get_delivery_address()
        assert any(line.strip() for line in address_lines)


@pytest.mark.ui
class TestDownloadInvoice:
    """TC 24 — Download Invoice After Purchase Order"""

    def test_invoice_file_is_downloaded(
        self,
        registered_page: Page,
        settings: Settings,
    ) -> None:
        add_product_and_checkout(registered_page, settings)
        checkout = CheckoutPage(page=registered_page, settings=settings)
        checkout.is_loaded()
        checkout.place_order()
        payment = PaymentPage(page=registered_page, settings=settings)
        payment.is_loaded()
        payment.fill_payment()
        payment.confirm_payment()
        filename = payment.download_invoice()
        assert filename
