import PySimpleGUI as sg

from utils.config import settings

from .order import layout_order, handler_order


def make_main_window() -> sg.Window:
    sg.theme(settings.main_themes)

    # padding_bottom = (0, 0)
    # size_menu_bottom = (13, 1)

    order_tab = layout_order.layout()

    layout = order_tab

    window = sg.Window(
        'Помошник сервисного центра',
        layout,
        auto_size_buttons=False,
        resizable=True,
        font=settings.font_window,
        finalize=True)

    return window


def start_app():
    window = make_main_window()

    while True:
        event, values = window.read()
        if settings.debug:
            print(event, "values:", values)
        if event == sg.WIN_CLOSED:
            break
        handler_order.handle(window, event, values)
    window.close()
