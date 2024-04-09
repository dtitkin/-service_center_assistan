import enum
from itertools import cycle


class TaskType(str, enum.Enum):
    ORDER_PRODUCTS = "Заказ товаров"
    AVIABLE_PRODUCTS = "Остатки товаров"
    GET_SUMMARY_INFORMATION = "Сводная информация"


class OrderCategory(str, enum.Enum):
    POINT_PRODUCTS = "Балловые товары",
    COUPON_PRODUCTS = "Купонные товары",
    STOCK_PRODUCTS = "Остатки РФ"


class ButtonOrderState(str, enum.Enum):
    EDIT_ORDER = "Корректировать заказ"
    INPUT_ADRESS = "Ввести адрес"
    SAVE_ORDER = "Записать заказ на сайт и отпарвить его"
    RETURN_TO_EDIT_ORDER = "Вернуться на страницу коррекции заказа"

    @classmethod
    def get_button_order_metadata(cls):
        return [cycle(cls), cls.EDIT_ORDER]
