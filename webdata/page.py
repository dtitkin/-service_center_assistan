
from utils.app_type import (
    BackofficeData,
    Tables_by_OrderCategory,
    ProductsTable,
    Decimal)

from utils.addres_data import Addres

from .locators import (
    LoginPage_locators,
    BackofficePage_locators,
    NewOrderPage_locators,
    WarehouseSelectionPage_locators,
    FillAdressPage_locators)


from .helpers import (
    click_all_next_button,
    get_table_data,
    set_table_data,
    _BasePage,
    _BaseElement,
    _BaseButton,
    click,
    )

from utils.app_enum import TaskType
from utils.config import settings


class LoginPage(_BasePage):
    field_login = _BaseElement(LoginPage_locators.LOGIN)
    field_password = _BaseElement(LoginPage_locators.PASSWORD)
    come_in_button = _BaseButton(LoginPage_locators.OK_BUTTON)

    def handle(self, request: list[TaskType]):
        self.field_login = self.login
        self.field_password = self.password
        self.come_in_button = click()
        return super().handle(request)


class BackofficePage(_BasePage):
    inventory = _BaseElement(BackofficePage_locators.INVENTORY_LINK)
    paid_inventory = _BaseElement(BackofficePage_locators.PAID_INVENTORY_LINK)
    orders_maid = _BaseElement(BackofficePage_locators.ORDERS_MADE_LINK)

    order_link = _BaseButton(BackofficePage_locators.ORDER_LINK)

    def get_table_from_page(self) -> BackofficeData:
        return BackofficeData(
            Decimal(self.inventory if self.inventory else 0),
            Decimal(self.paid_inventory if self.paid_inventory else 0),
            Decimal(self.orders_maid if self.orders_maid else 0)
            )

    def handle(self, request: list[TaskType]):

        if TaskType.GET_SUMMARY_INFORMATION in request:
            self.result_all_page.back_ofice_data = self.get_table_from_page()

        self.order_link = click()
        return super().handle(request)


class WarehouseSelectionPage(_BasePage):
    next_button = _BaseButton(WarehouseSelectionPage_locators.NEXT_BUTTON)

    def handle(self, request: list[TaskType]):
        self.next_button = click()
        return super().handle(request)


class NewOrderPage(_BasePage):
    other_block = _BaseElement(NewOrderPage_locators.OTHER_LINK)
    summary_txt = _BaseElement(NewOrderPage_locators.SUMMARY_TEXT)
    next_button = _BaseButton(WarehouseSelectionPage_locators.NEXT_BUTTON)

    def get_table_all_categories(self) -> Tables_by_OrderCategory:
        # ожидание прогрузки всего списка
        _ = self.other_block

        table = Tables_by_OrderCategory()
        categories = self.driver.find_elements(*NewOrderPage_locators.ALL_LINK)
        quantiti_category = len(categories)
        for i, elem_cat in enumerate(categories, 1):
            if self.thread_queue:
                self.thread_queue.put(('COUNTER', (i, quantiti_category)))

            data_cat = elem_cat.get_attribute(NewOrderPage_locators.CATEGORIES_ATRIBUTE)
            if not table.check_category(data_cat):
                continue

            elem_cat.click()
            category_name = elem_cat.text

            have_error = click_all_next_button(self.driver, NewOrderPage_locators.SHOW_MORE_LINK)
            if settings.debug:
                print(category_name, have_error)

            if have_error["have_error"]:
                # TODO
                if settings.debug:
                    print(f" ошибка в категории: {elem_cat.text}")
                    print(have_error)

            table.add_table(
                data_cat,
                get_table_data(
                    self.driver,
                    NewOrderPage_locators.ALL_GOODS_LINE,
                    category_name,
                    data_cat,
                    True,
                    False))
            if table.check_debug():
                break

        return table

    def set_order_table(self) -> Tables_by_OrderCategory:
        _ = self.other_block

        categories = self.driver.find_elements(*NewOrderPage_locators.ALL_LINK)
        quantiti_category = len(categories)

        table = Tables_by_OrderCategory()

        # переводим список списков в словарь номер категории: строки таблицы товаров
        # TODO высокая связанность интерфейса и бизнес логики. Нужно сменить номера
        map_order_row = {key: item
                         for key in [x.category_number for x in self.order_table if x.order > 0]
                         for item in [[y for y in self.order_table if y.order > 0 and y.category_number == key]]}

        for i, elem_cat in enumerate(categories, 1):

            if self.thread_queue:
                self.thread_queue.put(('COUNTER', (i, quantiti_category)))

            data_cat = elem_cat.get_attribute(NewOrderPage_locators.CATEGORIES_ATRIBUTE)
            if not table.check_category(data_cat):
                continue
            order_rows: ProductsTable = map_order_row.get(data_cat)
            if not order_rows:
                continue

            elem_cat.click()

            have_error = click_all_next_button(self.driver, NewOrderPage_locators.SHOW_MORE_LINK)
            if have_error["have_error"]:
                # TODO
                if settings.debug:
                    print(f" ошибка в категории: {elem_cat.text}")
                    print(have_error)

            table.add_table(
                data_cat,
                set_table_data(
                    self.driver,
                    NewOrderPage_locators.ALL_GOODS_LINE,
                    NewOrderPage_locators.INPUT_ORDER,
                    NewOrderPage_locators.product_line,
                    order_rows,
                    self.summary_txt)
            )
        return table

    def handle(self, request: list[TaskType]):
        if TaskType.AVIABLE_PRODUCTS in request:
            self.result_all_page.aviable_products = self.get_table_all_categories()
        elif TaskType.ORDER_PRODUCTS in request:
            self.result_all_page.ordered_products = self.set_order_table()
            self.next_button = click()

        return super().handle(request)


class FillAdressPage(_BasePage):
    fio = _BaseElement(FillAdressPage_locators.FIO, delete_all_in_inpit=True)
    phone = _BaseElement(FillAdressPage_locators.PHONE, delete_all_in_inpit=True)
    address = _BaseElement(FillAdressPage_locators.ADDRES, delete_all_in_inpit=True)
    post_index = _BaseElement(FillAdressPage_locators.POST_INDEX, delete_all_in_inpit=True)
    note = _BaseElement(FillAdressPage_locators.NOTE, delete_all_in_inpit=True)
    next_button = _BaseButton(FillAdressPage_locators.NEXT_BUTTON)

    def fill_adress(self):
        addres = Addres()
        self.fio = addres.fio
        self.phone = addres.phone
        self.address = addres.addres
        self.post_index = addres.post_index
        self.note = addres.note

    def handle(self, request: list[TaskType]):
        if TaskType.ORDER_PRODUCTS in request:
            self.fill_adress()
            # self.next_button = click()

        return super().handle(request)
