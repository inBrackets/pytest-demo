from playwright.sync_api import Page

from core.config import Settings
from products.pages.cart_page import CartPage
from products.pages.product_page import ProductPage


def add_product_and_checkout(page: Page, settings: Settings) -> None:
    """Helper: add first product to cart and proceed to checkout page."""
    product_pg = ProductPage(page=page, settings=settings)
    product_pg.navigate()
    product_pg.add_to_cart(index=0)
    product_pg.view_cart_from_modal()
    CartPage(page=page, settings=settings).proceed_to_checkout()
