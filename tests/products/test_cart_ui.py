import allure
import pytest
from playwright.sync_api import Page

from core.config import Settings
from products.pages.cart_page import CartPage
from products.pages.home_page import HomePage
from products.pages.product_detail_page import ProductDetailPage
from products.pages.product_page import ProductPage
from users.pages.login_page import LoginPage


@allure.feature("Shopping Cart")
@allure.story("Add Products")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ui
@pytest.mark.smoke
class TestAddProductsToCart:
    """TC 12 — Add Products in Cart"""

    def test_two_products_appear_in_cart(
        self, product_page: ProductPage, cart_page: CartPage
    ) -> None:
        product_page.navigate()
        product_page.add_to_cart(index=0)
        product_page.continue_shopping()
        product_page.add_to_cart(index=1)
        product_page.view_cart_from_modal()
        cart_page.is_loaded()
        assert cart_page.get_product_count() >= 2

    def test_cart_shows_correct_product_names(
        self, product_page: ProductPage, cart_page: CartPage
    ) -> None:
        product_page.navigate()
        product_page.add_to_cart(index=0)
        product_page.view_cart_from_modal()
        cart_page.is_loaded()
        assert len(cart_page.get_product_names()) > 0


@allure.feature("Shopping Cart")
@allure.story("Product Quantity")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.ui
class TestProductQuantityInCart:
    """TC 13 — Verify Product Quantity in Cart"""

    def test_quantity_4_is_reflected_in_cart(
        self, product_detail_page: ProductDetailPage, cart_page: CartPage
    ) -> None:
        cart_page.clear_cart()
        product_detail_page.navigate_to(product_id=1)
        product_detail_page.set_quantity(4)
        product_detail_page.add_to_cart()
        product_detail_page.view_cart()
        cart_page.is_loaded()
        quantities = cart_page.get_quantities()
        assert 4 in quantities


@allure.feature("Shopping Cart")
@allure.story("Remove Product")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.ui
class TestRemoveProductFromCart:
    """TC 17 — Remove Products From Cart"""

    def test_product_removed_from_cart(
        self, product_page: ProductPage, cart_page: CartPage
    ) -> None:
        product_page.navigate()
        product_page.add_to_cart(index=0)
        product_page.view_cart_from_modal()
        cart_page.is_loaded()
        count_before = cart_page.get_product_count()
        cart_page.remove_product(index=0)
        count_after = cart_page.get_product_count()
        assert count_after < count_before


@allure.feature("Shopping Cart")
@allure.story("Cart Persistence After Login")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.ui
class TestSearchAndVerifyCartAfterLogin:
    """TC 20 — Search Products and Verify Cart After Login"""

    def test_cart_products_persist_after_login(
        self, unauthenticated_page: Page, settings: Settings, live_account: dict[str, str]
    ) -> None:
        product_pg = ProductPage(page=unauthenticated_page, settings=settings)
        product_pg.navigate()
        product_pg.search("Blue Top")
        product_pg.add_to_cart(index=0)
        product_pg.view_cart_from_modal()

        cart = CartPage(page=unauthenticated_page, settings=settings)
        cart.is_loaded()
        names_before = cart.get_product_names()

        LoginPage(page=unauthenticated_page, settings=settings).navigate().login(
            username=live_account["email"],
            password=live_account["password"],
        )

        unauthenticated_page.goto(
            f"{settings.ui_base_url}/view_cart", wait_until="domcontentloaded"
        )
        cart.is_loaded()
        assert cart.get_product_names() == names_before


@allure.feature("Shopping Cart")
@allure.story("Recommended Items")
@allure.severity(allure.severity_level.MINOR)
@pytest.mark.ui
class TestAddRecommendedItemToCart:
    """TC 22 — Add to Cart from Recommended Items"""

    def test_recommended_item_added_to_cart(
        self, home_page: HomePage, cart_page: CartPage
    ) -> None:
        home_page.navigate()
        home_page.scroll_to_bottom()
        home_page.add_recommended_to_cart(index=0)
        home_page.view_cart_from_modal()
        cart_page.is_loaded()
        assert cart_page.get_product_count() >= 1
