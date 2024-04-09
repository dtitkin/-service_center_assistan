
from selenium.webdriver.common.by import By

type Locator = tuple[By, str]
type Products_category = tuple[str]


class LoginPage_locators():
    LOGIN: Locator = (By.NAME, 'login')
    PASSWORD: Locator = (By.NAME, 'passwd')
    OK_BUTTON: Locator = (By.XPATH, '//button[@type="submit"]')


class BackofficePage_locators():
    INVENTORY_LINK: Locator = (By.XPATH, "//a[@href='#admin/objects/remain']")
    PAID_INVENTORY_LINK: Locator = (By.XPATH, "//a[@href='/do.vshow#index/history/trmoneys']")
    ORDERS_MADE_LINK: Locator = (By.XPATH, "//a[@href='/do.vshow#admin/shop/move']")
    ORDER_LINK: Locator = (By.LINK_TEXT, "Заказать продукцию")


class NewOrderPage_locators():
    OTHER_LINK: Locator = ((By.LINK_TEXT, "(купон) Другое"))
    SHOW_MORE_LINK: Locator = (By.LINK_TEXT, "Показать еще...")
    ALL_GOODS_LINE: Locator = (By.CLASS_NAME, "goods-item")
    ALL_LINK: Locator = (By.XPATH, "//a[@href='#admin/shop/chgoods']")
    INPUT_ORDER: Locator = (By.TAG_NAME, "input")
    CATEGORIES_ATRIBUTE = 'data-cat'

    @staticmethod
    def category_link(number_category: str) -> Locator:
        return (By.XPATH, f"//a[@data-cat='{number_category}']")

    @staticmethod
    def product_line(product_code: str) -> Locator:
        return (By.XPATH, f"//tr[@class='goods-item' and @data-id={product_code}']")

    POINT_CATEGORYS: Products_category = (
        "3", "5", "4", "6", "7", "8", "9", "12", "13", "10")
    STOCK_CATEGORYS: Products_category = ("17",)
    COUPON_CATEGORYS: Products_category = (
        "18", "19", "20", "21", "22", "23", "24", "26", "27", "28", "25", "30", "32")
    OTHER_CATEGORYS: Products_category = ("cart", 'root', "1", "14", None)


class WarehouseSelectionPage_locators():
    NEXT__BUTTON = (By.CLASS_NAME, "btn-success")
