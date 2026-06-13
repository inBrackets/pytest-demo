import pytest

from ae_account.api.ae_account_client import AeAccountClient
from ae_account.models.ae_account_model import AeCreateAccountRequest
from checkout.pages.checkout_page import CheckoutPage
from checkout.pages.payment_page import PaymentPage
from products.pages.cart_page import CartPage
from products.pages.product_page import ProductPage
from users.pages.login_page import LoginPage


@pytest.fixture
def checkout_page(page, settings) -> CheckoutPage:
    return CheckoutPage(page=page, settings=settings)


@pytest.fixture
def payment_page(page, settings) -> PaymentPage:
    return PaymentPage(page=page, settings=settings)


@pytest.fixture
def registered_page(unauthenticated_page, settings, disposable_credentials, api_context):
    """Page logged in with a freshly created temp account."""
    AeAccountClient(api_context, settings).create_account(
        AeCreateAccountRequest.make(
            name=disposable_credentials["name"],
            email=disposable_credentials["email"],
            password=disposable_credentials["password"],
        )
    )
    LoginPage(unauthenticated_page, settings).navigate().login(
        username=disposable_credentials["email"],
        password=disposable_credentials["password"],
    )
    yield unauthenticated_page


def add_product_and_checkout(page, settings):
    """Helper: add first product to cart and proceed to checkout page."""
    product_pg = ProductPage(page=page, settings=settings)
    product_pg.navigate()
    product_pg.add_to_cart(index=0)
    product_pg.view_cart_from_modal()
    CartPage(page=page, settings=settings).proceed_to_checkout()
