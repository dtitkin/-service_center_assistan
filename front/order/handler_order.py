import PySimpleGUI as sg

from datetime import datetime
import queue

from middle.stock_logic import get_stock,  send_order, SummaryOrder
from utils.config import settings
from utils.addres_data import Addres
from utils.app_enum import ButtonOrderState

from utils.app_type import (
    ProductsTable,
    GoodsTable)

from .layout_order import window_input_number


THREAD_KEY = '-GET_STOCK_THREAD-'
THREAD_EXIT = '-GET_STOCK_END-'
THREAD_INFO = '-GET_STOCK_INFO-'
TREAD_DATA_EXIT = '-GET_STOCK_DATA_END-'

TREAD_ORDER_DATA_EXIT = '-ORDER_DATA_END-'


has_open_window = False


def handle(window: sg.Window, event, value):

    if event == '-GET_STOCK-':
        window['-TXT_DATE-'].update(visible=False)
        window['-PROGRES-'].update(visible=True, current_count=0)
        order_queue = queue.Queue()
        window.start_thread(
            lambda: _info_from_thread(
                window,
                order_queue,
                THREAD_KEY,
                THREAD_INFO),
            (THREAD_KEY, THREAD_EXIT))

        window.start_thread(
            lambda: get_stock(order_queue),
            (THREAD_KEY, TREAD_DATA_EXIT))

    elif event[0] == THREAD_KEY:
        page_data = value.get((THREAD_KEY, THREAD_INFO))

        if event[1] == THREAD_INFO and page_data:
            if page_data[0] == 'COUNTER':
                # пришла информация о прогреессе обработки категорий
                max_value = page_data[1][1]
                iter_value = page_data[1][0]
                now_value = settings.size_progresbar/max_value*iter_value
                window['-PROGRES-'].update(current_count=now_value)

            elif page_data[0] == 'DATA':
                window['-SELECT_CATEGORY-'].metadata = page_data[1].aviable_products
                window.write_event_value('-SELECT_CATEGORY-', value['-SELECT_CATEGORY-'])

            elif page_data[0] == 'ORDER':
                category = value['-SELECT_CATEGORY-']
                # выеведем текст с товарами у котороых поменялось количество
                category_table: ProductsTable = page_data[1].ordered_products.get_category_table(category)
                info_txt = ""
                for row in category_table:
                    if row.order != 0 and row.order < row.set_order:
                        info_txt += f"{row.goods_number}  {row.goods_number}  {row.order}: {row.set_order}\n"
                if info_txt:
                    window['-INFO_ORDER-'].update(value=info_txt)

        elif event[1] == TREAD_DATA_EXIT:
            window['-PROGRES-'].update(visible=False)
            window['-TXT_DATE-'].update(
                value=datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
                visible=True)

    elif event == '-SELECT_CATEGORY-':
        category = value[event]
        if window['-SELECT_CATEGORY-'].metadata:
            # products_tables: ProductsTable = window['-SELECT_CATEGORY-'].metadata[category]
            # window['-TABLE-'].update(values=[x.aslist() for x in products_tables])
            window['-TABLE-'].update(values=window['-SELECT_CATEGORY-'].metadata.get_front_table(category))

    elif event[0] == '-TABLE-':
        category = value['-SELECT_CATEGORY-']
        state_button = window['-SEND_ORDER-'].metadata[1]

        normal_state = state_button == ButtonOrderState.EDIT_ORDER

        if (event[1] == '+CLICKED+' and event[2][0] is not None and event[2][0] > -1 and normal_state):

            global has_open_window
            if not has_open_window:
                has_open_window = True
                # кликнули по строке
                if window['-SELECT_CATEGORY-'].metadata:
                    number_data_row = event[2][0]
                    row_data: GoodsTable = (
                        window['-SELECT_CATEGORY-'].metadata.get_row_form_table(category, number_data_row))

                    name_product = row_data.goods_name
                    max_number = row_data.quantity_supplier
                    input_val = window_input_number(name_product, max_number)
                    has_open_window = False
                    if input_val != row_data.order:
                        row_data.order = input_val
                        window.write_event_value('-SELECT_CATEGORY-', value['-SELECT_CATEGORY-'])

    elif event == '-CORRECT_ORDER-':
        window['-SEND_ORDER-'].metadata = ButtonOrderState.get_button_order_metadata()
        _set_edit_order_window(window, value)

    elif event == '-SEND_ORDER-':
        category = value['-SELECT_CATEGORY-']
        state_after_click: ButtonOrderState = next(window['-SEND_ORDER-'].metadata[0])
        window['-SEND_ORDER-'].metadata[1] = state_after_click
        if state_after_click == ButtonOrderState.EDIT_ORDER:
            _set_edit_order_window(window, value)

        elif state_after_click == ButtonOrderState.INPUT_ADRESS:
            # показываю таблицу с товарами только из заказа
            # блокируем выбор категории
            window['-CORRECT_ORDER-'].update(visible=True)
            window['-ADRRES_SECTION-'].update(visible=True)
            window['-SELECT_CATEGORY-'].update(readonly=True)
            if window['-SELECT_CATEGORY-'].metadata:
                window['-TABLE-'].update(values=window['-SELECT_CATEGORY-'].metadata.get_front_table(category, 'order'))
            window['-SEND_ORDER-'].update(text="Отправить >>")
            _restore_addres_value(window)

        elif state_after_click == ButtonOrderState.SAVE_ORDER:
            # проверяем поля на заполненность
            if not _validate_adress_section(window, event, value):
                _ = next(window['-SEND_ORDER-'].metadata[0])
                _ = next(window['-SEND_ORDER-'].metadata[0])
            else:
                # вызываем поток заполнения и отправки заказа
                window['-PROGRES-'].update(visible=True, current_count=0)
                order_queue = queue.Queue()
                window.start_thread(
                    lambda: _info_from_thread(
                        window,
                        order_queue,
                        THREAD_KEY,
                        THREAD_INFO),
                    (THREAD_KEY, THREAD_EXIT))

                window.start_thread(
                    lambda: send_order(
                        order_queue,
                        window['-SELECT_CATEGORY-'].metadata.get_category_table(category)
                        ), (THREAD_KEY, TREAD_ORDER_DATA_EXIT))

                # меняем имя нокпки на ОК
                window['-SEND_ORDER-'].update(text="ОК")
                window['-CORRECT_ORDER-'].update(visible=False)
                window['-INFO_ORDER_SECTION-'].update(visible=True)

    if event[0] == '-TABLE-' or event == '-SELECT_CATEGORY-':
        category = value['-SELECT_CATEGORY-']
        _set_row_colors_summary(category, window)


def _info_from_thread(
    window: sg.Window,
    thread_queue: queue.Queue,
    thread_key: str,
    thread_incoming_data: str
     ):

    while True:
        data = thread_queue.get()
        if data[0] == 'END':
            break
        window.write_event_value((thread_key, thread_incoming_data), data)


def _set_row_colors_summary(category: str, window: sg.Window):
    summary = SummaryOrder()
    update_row_color = []
    if not window['-SELECT_CATEGORY-'].metadata:
        return
    products_tables: ProductsTable = window['-SELECT_CATEGORY-'].metadata.get_category_table(category)
    for number_data_row, row in enumerate(products_tables):
        if row.order != 0:
            update_row_color.append(((number_data_row, settings.order_row_colors)))
            summary.summary_order(row)

    if len(update_row_color) > 0:
        window['-COUNT_SCU-'].update(f'{summary.count_scu} шт.')
        window['-COUNT_THING-'].update(f'{summary.count_thing} уп.')
        window['-SUM_ORDER_PRODUCT-'].update(f'{float(summary.sum_order_product):_} руб.'.replace('_', ' '))
        window['-BALLS_PRODUCT-'].update(f'{summary.balls_product}')

        window['-TABLE-'].update(row_colors=update_row_color)


def _validate_adress_section(window, event, value) -> bool:
    validate_rule = {
        '-IN_FIO-': '-L_FIO-',
        '-IN_PHONE-': '-L_PHONE-',
        '-IN_ADDRES-': '-L_ADDRES-',
        '-IN_POST_INDEX-': '-L_POST_INDEX-',
        '-IN_NOTE-': '-L_NOTE-'
        }
    addres = Addres()
    ok = True
    for field_key, label_key in validate_rule.items():
        if not value[field_key]:
            ok = False
            window[label_key].update(text_color='red')
        else:
            window[label_key].update(text_color=sg.theme_element_text_color())
            # TODO
            match field_key:
                case '-IN_FIO-':
                    addres.fio = value[field_key]
                case '-IN_PHONE-':
                    addres.phone = value[field_key]
                case '-IN_ADDRES-':
                    addres.addres = value[field_key]
                case '-IN_POST_INDEX-':
                    addres.post_index = value[field_key]
                case '-IN_NOTE-':
                    addres.note = value[field_key]
    return ok


def _restore_addres_value(window):
    addres = Addres()
    window['-IN_FIO-'].update(value=addres.fio)
    window['-IN_PHONE-'].update(value=addres.phone)
    window['-IN_ADDRES-'].update(value=addres.addres)
    window['-IN_POST_INDEX-'].update(value=addres.post_index)
    window['-IN_NOTE-'].update(value=addres.note)


def _set_edit_order_window(window, value):
    window['-CORRECT_ORDER-'].update(visible=False)
    window['-ADRRES_SECTION-'].update(visible=False)
    window['-INFO_ORDER_SECTION-'].update(visible=False)
    window['-INFO_ORDER-'].update(value="")
    window['-SELECT_CATEGORY-'].update(readonly=False)
    window['-SEND_ORDER-'].update(text="Заказать >>")
    window.write_event_value('-SELECT_CATEGORY-', value['-SELECT_CATEGORY-'])
    window['-PROGRES-'].update(visible=False, current_count=0)
