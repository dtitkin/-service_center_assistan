import re
from collections.abc import Callable

from selenium import webdriver
from selenium.common.exceptions import (StaleElementReferenceException,  # noqa
                                        TimeoutException)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


from utils.config import settings

import queue

from utils.app_type import (
    PageResult,
    Tables_by_OrderCategory,
    ProductsTable,
    Locator,
    Decimal,
    GoodsTable)

from utils.app_enum import TaskType, OrderCategory


from .locators import (
    NewOrderPage_locators)


def click():
    return True


class _BasePage():
    result_all_page: PageResult = PageResult()

    def __init__(self, driver:  webdriver,
                 thread_queue: queue.Queue | None = None,
                 login: str = "",
                 password: str = "",
                 order_table: ProductsTable | None = None
                 ):
        self.driver = driver
        self.thread_queue = thread_queue
        self._next_handler = None
        self.login = login
        self.password = password
        self.order_table = order_table

    def set_next(self, next_hendler):
        self._next_handler = next_hendler
        return next_hendler

    def handle(self, request: list[TaskType]) -> PageResult:
        if self._next_handler:
            return self._next_handler.handle(request)

        return self.result_all_page


class _BaseElement():
    def __init__(self, locator: Locator, name_attribite=None):
        self.locator = locator
        self.name_attribite = name_attribite

    def __set__(self, obj, value):
        obj.driver.find_element(*self.locator).send_keys(value)

    def __get__(self, obj, owner):
        if not self.name_attribite:
            return obj.driver.find_element(*self.locator).text
        else:
            return (
                obj.driver.find_element(*self.locator)
                .get_attribute(self.name_attribite))


class _BaseButton():
    def __init__(self, locator: Locator):
        self.locator = locator

    def __set__(self, obj, value):
        button = obj.driver.find_element(*self.locator)
        button.click()


class _ReturnTable():

    def __init__(self):
        self.table: Tables_by_OrderCategory = {
            OrderCategory.POINT_PRODUCTS: [],
            OrderCategory.COUPON_PRODUCTS: [],
            OrderCategory.STOCK_PRODUCTS: []
            }
        self.stock_table = None

    def add_table(self, data_cat: str, data_table: ProductsTable):
        self.check_category(data_cat)

        self.table[self.stock_table].extend(data_table)

    def check_debug(self):
        if self.stock_table and settings.debug:
            if len(self.table[self.stock_table]) >= 10:
                return True
            else:
                return False

    def check_category(self, data_cat: str) -> bool:
        if data_cat in NewOrderPage_locators.POINT_CATEGORYS:
            self.stock_table = OrderCategory.POINT_PRODUCTS
        elif data_cat in NewOrderPage_locators.COUPON_CATEGORYS:
            self.stock_table = OrderCategory.COUPON_PRODUCTS
        elif data_cat in NewOrderPage_locators.STOCK_CATEGORYS:
            self.stock_table = OrderCategory.STOCK_PRODUCTS
        else:
            # TODO доделать возврать информации о том что есть не взятые категориии
            return False
        return True


def click_all_next_button(driver: webdriver, locator: Locator):
    """ находит элемент на экране и щелкает на него пока он не исчезнеет
        Нужно для кнопки Показать Еще...
    """
    wait = WebDriverWait(driver, timeout=settings.until_wait)
    do_it = True
    have_error = {"have_error": False, "erros_on_click": [], "max_clicks": 0}
    count_press = 0
    while do_it:
        try:
            # elem = wait.until(EC.visibility_of_element_located(locator))
            elem = wait.until(EC.any_of(EC.element_to_be_clickable(locator),
                              EC.visibility_of_element_located(locator)))
            elem.click()
            count_press += 1
        except TimeoutException:
            do_it = False
        except Exception:
            # print(elem)
            # print("!!!!!!!!!!!!!")
            # print(elem.is_displayed(), elem.is_enabled())
            have_error["have_error"] = True
            have_error["erros_on_click"].append(count_press+1)
        have_error["max_clicks"] = count_press
        return have_error


def get_table_data(
    driver: webdriver,
    locator: Locator,
    category_name: str,
    category_number: str,
    not_zero_supplier: bool,
    not_zero_service_center: bool
) -> ProductsTable:

    table = []
    wait = WebDriverWait(driver, timeout=settings.until_wait)

    do_it = True
    while do_it:
        try:
            goods = wait.until(EC.visibility_of_all_elements_located(locator))
            do_it = False
        except TimeoutException:
            do_it = True

    # goods = driver.find_elements(*locator)

    for i, good in enumerate(goods, 0):
        row = GoodsTable()

        row.category = category_name

        # try:
        columns = good.find_elements(By.CSS_SELECTOR, 'td')
        row.goods_number = good.get_attribute("data-id")
        # except StaleElementReferenceException:
        #     good = driver.find_elements(*locator)[i]
        #     columns = good.find_elements(By.CSS_SELECTOR, 'td')
        #     row.category = good.get_attribute("data-id")
        # первая колонка - коды, берем данные из строки

        # забираем текст со второй по четвертую колонку
        txt_col_1, txt_col_2, txt_col_3, txt_col_4 = map(
            lambda _: _.text, columns[1:5])

        # вторая колонка
        values = txt_col_1.split('\n')
        # TODO доделать обработку ошибки
        if len(values) < 3:
            if settings.debug:
                print("ОШИБКА ЗДЕСЬ", category_name, i, columns)

        row.goods_name = values[0]
        row.quantity_supplier = Re.get_int_end(values[1])
        row.quantity_service_center = Re.get_int_end(values[2])

        # третья колонка
        row.price_retail = Re.get_decimal_start(txt_col_2)

        # четвертая колонка
        row.price_service_center = Re.get_decimal_start(txt_col_3)

        # пятая колонка
        row.balls = Re.get_decimal_start(txt_col_4)

        row.category_number = category_number

        if ((not_zero_supplier and row.quantity_supplier > 0)
                or (not_zero_service_center and row.quantity_service_center > 0)):
            table.append(row)

    return table


def set_table_data(driver: webdriver,
                   all_goods_locator: Locator,
                   input_order: Locator,
                   line_goods:  Callable[[str], Locator],
                   order_table: ProductsTable) -> ProductsTable:

    """ По товарам одной кагории
        заполняет таблицу заказа на сайт
        возвращает таблицу с данными по которые были установленны в заказ

    Args:
        driver (webdriver): _description_
        locator (Locator): _description_
        order_rows (DataTable): _description_

    Returns:
        Table: _description_
    """

    table: ProductsTable = []
    wait = WebDriverWait(driver, timeout=settings.until_wait)

    # дождемся прогрузки страницы с товарами
    do_it = True
    while do_it:
        try:
            wait.until(EC.visibility_of_all_elements_located(all_goods_locator))
            do_it = False
        except TimeoutException:
            do_it = True

    # Заполним значения по каждой строкке с товарам
    # если остаток на сайте сейчас меньше чем тот котороый мы заказываем
    # то ставим остаток который на сайте
    for good_row in order_table:

        line_product = driver.find_element(*line_goods(good_row.goods_number))
        columns = line_product.find_elements(By.CSS_SELECTOR, 'td')

        # из второй колонки получаем остатки
        values = columns[1].text.split('\n')
        quantity_service_center = Re.get_int_end(values[2])

        to_order = good_row.order if quantity_service_center >= good_row.order else quantity_service_center

        input_order = columns[5].find_element(*input_order)
        input_order.send_keys(to_order)
        good_row.set_order = to_order
        table.append(good_row)
    return table


class Re():
    _re_int_end_digit = r'-?\d+$'
    _re_decim_start_digit = r'(^\d+\.\d+)|(^\d+)'

    @staticmethod
    def _re_find_number(source: str, pattern: str, number_function: Callable) -> str:
        match = re.search(pattern, source)
        if match:
            return number_function(match.group())
        else:
            return number_function(0)

    @classmethod
    def get_int_end(cls, source: str) -> int:
        return cls._re_find_number(source, cls._re_int_end_digit, int)

    @classmethod
    def get_decimal_start(cls, source: str) -> Decimal:
        return cls._re_find_number(source, cls._re_decim_start_digit, Decimal)
