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

    @classmethod
    def category_by_value(cls, value: str):
        # TODO нормальный методо перебора атрибутов класса через dir vars callable getatr
        # https://translated.turbopages.org/proxy_u/en-ru.ru.13cd55e5-661502f0-12da7969-74722d776562/https/stackoverflow.com/questions/5969806/print-all-properties-of-a-python-class?__ya_mt_enable_static_translations=1
        CATEGORIES = {cat.value: cat for cat in cls}
        return CATEGORIES.get(value)


class ButtonOrderState(str, enum.Enum):
    EDIT_ORDER = "Корректировать заказ"
    INPUT_ADRESS = "Ввести адрес"
    SAVE_ORDER = "Записать заказ на сайт и отправить его"

    @classmethod
    def get_button_order_metadata(cls):
        ckl = cycle(cls)
        _ = next(ckl)
        return [ckl, cls.EDIT_ORDER]
