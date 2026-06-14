import allure
import pytest

from products.pages.cart_page import CartPage
from products.pages.home_page import HomePage


@allure.feature("Subscription")
@allure.story("Subscribe from Home")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.ui
class TestSubscriptionOnHomePage:
    """TC 10 — Verify Subscription in Homepage"""

    def test_subscription_success_shown(self, home_page: HomePage) -> None:
        home_page.navigate()
        home_page.scroll_to_bottom()
        home_page.subscribe("subscriber@test.com")


@allure.feature("Subscription")
@allure.story("Subscribe from Cart")
@allure.severity(allure.severity_level.MINOR)
@pytest.mark.ui
class TestSubscriptionOnCartPage:
    """TC 11 — Verify Subscription in Cart Page"""

    def test_subscription_success_on_cart(self, cart_page: CartPage) -> None:
        cart_page.navigate()
        cart_page.subscribe("cartsub@test.com")
