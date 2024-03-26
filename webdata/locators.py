
from selenium.webdriver.common.by import By

from utils.app_type import Locator, Products_category


class LoginPage_locators():
    LOGIN: Locator = (By.NAME, 'login')
    PASSWORD: Locator = (By.NAME, 'passwd')
    OK_BUTTON: Locator = (By.CLASS_NAME, "jss99")


class BackofficePage_locators():
    INVENTORY_LINK: Locator = (By.XPATH, "//a[@href='#admin/objects/remain']")
    PAID_INVENTORY_LINK: Locator = (By.XPATH, "//a[@href='/do.vshow#index/history/trmoneys']")
    ORDERS_MADE_LINK: Locator = (By.XPATH, "//a[@href='/do.vshow#admin/shop/move']")
    ORDER_LINK: Locator = (By.LINK_TEXT, "Заказать продукцию")


class NewOrderPage_locators():
    OTHER_LINK: Locator = ((By.LINK_TEXT, "(купон) Другое"))
    SHOW_MORE_LINK: Locator = (By.LINK_TEXT, "Показать еще...")
    GOODS_LINE: Locator = (By.CLASS_NAME, "goods-item")

    @staticmethod
    def category_link(number_category: str) -> Locator:
        return (By.XPATH, f"//a[@data-cat='{number_category}']")

    POINT_CATEGORYS: Products_category = (
        "3", "5", "4", "6", "7", "8", "9", "12", "13", "10")
    LEFTOVER_CATEGORYS: Products_category = ("17",)
    COUPON_CATEGORYS: Products_category = (
        "18", "19", "20", "21", "22", "23", "24", "26", "27", "28", "25", "30")


class WarehouseSelectionPage_locators():
    NEXT__BUTTON = (By.CLASS_NAME, "btn-success")
