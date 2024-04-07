import PySimpleGUI as sg

from datetime import datetime
import queue

from middle.stock_logic import get_stock, SummaryOrder
from utils.config import settings
from utils.app_enum import OrderCategory
from .layout_order import window_input_number


THREAD_KEY = '--GET_STOCK_THREAD-'
THREAD_EXIT = '-GET_STOCK_END-'
THREAD_INFO = '-GET_STOCK_INFO-'
TREAD_DATA_EXIT = '-GET_STOCK_DATA_END-'
CATEGORIES = {cat.value: cat for cat in OrderCategory}


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
            window['-TABLE-'].update(values=window['-SELECT_CATEGORY-'].metadata[category][:-2])

    elif event[0] == '-TABLE-':
        category = CATEGORIES[value['-SELECT_CATEGORY-']]
        if event[1] == '+CLICKED+' and (event[2][0] is not None and event[2][0] > -1):
            # кликнули по строке
            if window['-SELECT_CATEGORY-'].metadata:
                number_data_row = event[2][0]
                row_data = window['-SELECT_CATEGORY-'].metadata[category][number_data_row]
                name_product = row_data[2]
                max_number = row_data[6]
                input_val = window_input_number(name_product, max_number)
                if input_val != row_data[7]:
                    row_data[7] = input_val
                    window['-TABLE-'].update(
                        values=window['-SELECT_CATEGORY-'].metadata[category],)
    elif event == '-SEND_ORDER-':
        visible_correct = not window['-SEND_ORDER-'].metadata
        window['-SEND_ORDER-'].metadata = visible_correct
        window['-CORRECT_ORDER-'].update(visible=visible_correct)
        window['-ADRRES_SECTION-'].update(visible=visible_correct)

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
    for number_data_row, row in enumerate(window['-SELECT_CATEGORY-'].metadata[category]):
        if row[7] != 0:
            update_row_color.append(((number_data_row, settings.order_row_colors)))
            summary.summary_order(row)

    if len(update_row_color) > 0:
        window['-COUNT_SCU-'].update(f'{summary.count_scu} шт.')
        window['-COUNT_THING-'].update(f'{summary.count_thing} уп.')
        window['-SUM_ORDER_PRODUCT-'].update(f'{float(summary.sum_order_product):_} руб.'.replace('_', ' '))
        window['-BALLS_PRODUCT-'].update(f'{summary.balls_product}')

        window['-TABLE-'].update(row_colors=update_row_color)
