import re
from collections.abc import Callable

from selenium import webdriver
from selenium.common.exceptions import (StaleElementReferenceException,  # noqa
                                        TimeoutException)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from utils.app_type import Decimal, GoodsTable, Locator, Table, DataTable
from utils.config import settings


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
) -> Table:

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
                   line_goods:  Callable[[str], Locator],
                   input_order,
                   order_rows: DataTable) -> Table:

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

    table = []
    wait = WebDriverWait(driver, timeout=settings.until_wait)

    # дождемся прогрузки страницы с товарами
    do_it = True
    while do_it:
        try:
            goods = wait.until(EC.visibility_of_all_elements_located(all_goods_locator))
            do_it = False
        except TimeoutException:
            do_it = True


    # Заполним значения по каждой строкке с товарам
    # если остаток на сайте сейчас меньше чем тот котороый мы заказываем
    # то ставим остаток который на сайте
    for good_row in order_rows:
        row = GoodsTable()
        # TODO переделать ображешие по индексу в списке на человеческое
        product_code = good_row[1]

        line_product = driver.find_element(*line_goods(product_code))
        columns = line_product.find_elements(By.CSS_SELECTOR, 'td')

        # из второй колонки получаем остатки
        values =  columns[1].text.split('\n')
        quantity_service_center = Re.get_int_end(values[2])

        to_order = good_row[7] if  quantity_service_center >= good_row[7] else quantity_service_center





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
