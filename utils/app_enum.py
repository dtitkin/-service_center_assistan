import enum


class TaskType(str, enum.Enum):
    ORDER_PRODUCTS = "Заказ товаров"
    AVIABLE_PRODUCTS = "Остатки товаров"
    GET_SUMMARY_INFORMATION = "Сводная информация"


class OrderCategory(str, enum.Enum):
    POINT_PRODUCTS = "Балловые товары",
    COUPON_PRODUCTS = "Купонные товары",
    STOCK_PRODUCTS = "Остатки РФ"
