from collections import namedtuple
from collections.abc import Mapping, Sequence  # noqa
from dataclasses import dataclass
from decimal import Decimal

from selenium.webdriver.common.by import By
from .enumirate import OrderCategory

BackofficeData = namedtuple('BackofficeData',
                            ['inventory',
                             'paid_inventory',
                             'orders_maid'])

type Table = Mapping[OrderCategory, Sequence[GoodsTable]]
type Locator = tuple[By, str]
type Products_category = tuple[str]


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


@dataclass
class PageResult():
    back_ofice_data: BackofficeData | None = None
    aviable_products: Table | None = None
