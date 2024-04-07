from collections import namedtuple
from collections.abc import Mapping, Sequence  # noqa
from dataclasses import dataclass
from decimal import Decimal

from selenium.webdriver.common.by import By
from selenium import webdriver  # noqa
from .app_enum import OrderCategory

BackofficeData = namedtuple('BackofficeData',
                            ['inventory',
                             'paid_inventory',
                             'orders_maid'])

type Table = Mapping[OrderCategory, Sequence[GoodsTable]]
type Locator = tuple[By, str]
type Products_category = tuple[str]
type DataTable = Sequence[Sequence[int | str | Decimal]]


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
    set_order: Decimal = Decimal(0)

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


@dataclass
class PageResult():
    back_ofice_data: BackofficeData | None = None
    aviable_products: DataTable | None = None
