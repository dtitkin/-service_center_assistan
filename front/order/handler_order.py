import PySimpleGUI as sg

from datetime import datetime
import queue

from middle.stock_logic import get_stock,  send_order, SummaryOrder
from utils.config import settings
from utils.app_enum import OrderCategory, ButtonOrderState

from utils.app_type import (
    ProductsTable,
    GoodsTable)

from .layout_order import window_input_number


THREAD_KEY = '--GET_STOCK_THREAD-'
THREAD_EXIT = '-GET_STOCK_END-'
THREAD_INFO = '-GET_STOCK_INFO-'
TREAD_DATA_EXIT = '-GET_STOCK_DATA_END-'
CATEGORIES = {cat.value: cat for cat in OrderCategory}

has_open_window = False


def handle(window: sg.Window, event, value):
    order_queue = queue.Queue()

    if event == '-GET_STOCK-':
        window['-TXT_DATE-'].update(visible=False)
        window['-PROGRES-'].update(visible=True, current_count=0)

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

        elif event[1] == TREAD_DATA_EXIT:
            window['-PROGRES-'].update(visible=False)
            window['-TXT_DATE-'].update(
                value=datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
                visible=True)

    elif event == '-SELECT_CATEGORY-':
        category = CATEGORIES[value[event]]

        if window['-SELECT_CATEGORY-'].metadata:
            products_tables: ProductsTable = window['-SELECT_CATEGORY-'].metadata[category]
            window['-TABLE-'].update(values=[x.aslist() for x in products_tables])

    elif event[0] == '-TABLE-':
        category = CATEGORIES[value['-SELECT_CATEGORY-']]
        if event[1] == '+CLICKED+' and (event[2][0] is not None and event[2][0] > -1):
            global has_open_window
            if not has_open_window:
                has_open_window = True
                # кликнули по строке
                if window['-SELECT_CATEGORY-'].metadata:
                    number_data_row = event[2][0]
                    row_data: GoodsTable = window['-SELECT_CATEGORY-'].metadata[category][number_data_row]
                    name_product = row_data.goods_name
                    max_number = row_data.quantity_supplier
                    input_val = window_input_number(name_product, max_number)
                    has_open_window = False
                    if input_val != row_data.order:
                        row_data.order = input_val
                        window.write_event_value('-SELECT_CATEGORY-', value['-SELECT_CATEGORY-'])

    elif event == '-SEND_ORDER-':
        state_after_click: ButtonOrderState = next(window['-SEND_ORDER-'].metadata[0])
        window['-SEND_ORDER-'].metadata[1] = state_after_click
        if state_after_click == ButtonOrderState.EDIT_ORDER:
            window['-CORRECT_ORDER-'].update(visible=False)
            window['-ADRRES_SECTION-'].update(visible=False)
            window['-SEND_ORDER-'].update(text="Заказать >>")

        elif state_after_click == ButtonOrderState.INPUT_ADRESS:
            # показываю таблицу с товарами только из заказа
            # блокируем выбор категории
            window['-CORRECT_ORDER-'].update(visible=True)
            window['-ADRRES_SECTION-'].update(visible=True)

            window['-SELECT_CATEGORY-'].update(disabled=True)


        elif state_button == ButtonOrderState.SAVE_ORDER:
            window['-CORRECT_ORDER-'].update(visible=True)
            window['-ADRRES_SECTION-'].update(visible=True)
            window['-SEND_ORDER-'].update(text="Отправить >>")








        window['-CORRECT_ORDER-'].update(visible=True if state_button == 1 else False)
        window['-ADRRES_SECTION-'].update(visible=True if state_button in (1,2) else False)

    if event[0] == '-TABLE-' or event == '-SELECT_CATEGORY-':
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


def _set_row_colors_summary(category: OrderCategory, window: sg.Window):
    summary = SummaryOrder()
    update_row_color = []
    if not window['-SELECT_CATEGORY-'].metadata:
        return
    products_tables: ProductsTable = window['-SELECT_CATEGORY-'].metadata[category]
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
