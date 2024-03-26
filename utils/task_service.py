import enum


class TaskType(str, enum.Enum):
    ORDER_POINT_PRODUCTS = "Заказ балловые товары"
    ORDER_COUPON_PRODUCTS = "Заказ купонные товары"
    ORDER_LEFTOVERS_PRODUCTS = "Заказ остаточные товары"

    AVIABLE_POINT_PRODUCTS = "Остатки балловые товары"
    AVIABLE_COUPON_PRODUCTS = "Остатки купонные товары"
    AVIABLE_LEFTOVERS_PRODUCTS = "Остатки остаточные товары"

    GET_SUMMARY_INFORMATION = "Получить сводную информацию"
