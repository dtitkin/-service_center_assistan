from collections import namedtuple
from collections.abc import Mapping, Sequence  # noqa
from dataclasses import dataclass
from decimal import Decimal

from selenium import webdriver  # noqa
from .app_enum import OrderCategory
from utils.config import settings

BackofficeData = namedtuple('BackofficeData',
                            ['inventory',
                             'paid_inventory',
                             'orders_maid'])

from webdata.locators import (Locator, Products_category, NewOrderPage_locators)  # noqa

type ProductsTable = Sequence[GoodsTable]
type ProductsTableFront = Sequence[Sequence[int | str | Decimal]]


# type DataTable = Sequence[Sequence[int | str | Decimal]]


@dataclass
class GoodsTable():
    category = ""
    goods_number: str = ""
    goods_name: str = ""
    quantity_supplier: int = 0
    quantity_service_center: int = 0
    price_retail: Decimal = Decimal(0)
    price_service_center: Decimal = Decimal(0)
    balls: Decimal = Decimal(0)
    order: int = 0
    category_number: str = ""
    set_order: int = 0

    def aslist(self):
        return [
            self.category,
            self.goods_number,
            self.goods_name,
            self.price_retail,
            self.price_service_center,
            self.balls,
            self.quantity_supplier,
            self.order,
            self.set_order,
            self.category_number]


class Tables_by_OrderCategory():

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


@dataclass
class PageResult():
    back_ofice_data: BackofficeData | None = None
    aviable_products: Tables_by_OrderCategory | None = None
    ordered_products: Tables_by_OrderCategory | None = None
