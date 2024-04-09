import queue

from selenium import webdriver

from utils.config import settings
from utils.app_enum import TaskType
from utils.app_type import Decimal, GoodsTable, ProductsTable

from webdata.page import (
    LoginPage,
    BackofficePage,
    WarehouseSelectionPage,
    NewOrderPage)


def get_stock(thread_queue: queue.Queue):
    driver = webdriver.Chrome()
    driver.implicitly_wait(settings.implicitly_wait)

    driver.get(settings.login_uri)

    login_page = LoginPage(
        driver,
        thread_queue=thread_queue,
        login=settings.login,
        password=settings.password)

    back_ofice_page = BackofficePage(driver, thread_queue=thread_queue)
    werehouse_select_page = WarehouseSelectionPage(driver, thread_queue=thread_queue)
    new_order_page = NewOrderPage(driver, thread_queue=thread_queue)

    (login_page.set_next(back_ofice_page)
     .set_next(werehouse_select_page)
     .set_next(new_order_page))

    result = login_page.handle([
        TaskType.GET_SUMMARY_INFORMATION,
        TaskType.AVIABLE_PRODUCTS])

    # для фронта нужен список списков
    # for k, v in result.aviable_products.items():
    #    result.aviable_products[k] = [row.aslist() for row in v]

    thread_queue.put(('DATA', result))
    thread_queue.put(('END', 'END'))


def send_order(thread_queue: queue.Queue, order_table: ProductsTable):
    driver = webdriver.Chrome()
    driver.implicitly_wait(settings.implicitly_wait)

    driver.get(settings.login_uri)

    login_page = LoginPage(
        driver,
        thread_queue=thread_queue,
        login=settings.login,
        password=settings.password)

    back_ofice_page = BackofficePage(driver, thread_queue=thread_queue)
    werehouse_select_page = WarehouseSelectionPage(driver, thread_queue=thread_queue)
    new_order_page = NewOrderPage(driver, thread_queue=thread_queue, order_table=order_table)

    (login_page.set_next(back_ofice_page)
     .set_next(werehouse_select_page)
     .set_next(new_order_page))

    result = login_page.handle([TaskType.ORDER_PRODUCTS])

    thread_queue.put(('ORDER', result))
    thread_queue.put(('END', 'END'))


class SummaryOrder():
    def __init__(self,
                 count_scu: int = 0,
                 count_thing: int = 0,
                 sum_order_product: Decimal = Decimal(0),
                 balls_product: Decimal = Decimal(0)):

        self.count_scu = 0
        self.count_thing = 0
        self.sum_order_product = 0
        self.balls_product = 0

    def summary_order(self, row: GoodsTable):
        self.count_scu += 1
        self.count_thing += row.order
        self.sum_order_product += row.order * row.price_service_center
        self.balls_product += row.order * row.balls
