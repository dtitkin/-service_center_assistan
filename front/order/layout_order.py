import PySimpleGUI as sg

from utils.app_enum import OrderCategory, ButtonOrderState

from utils.config import settings
from utils.app_type import Decimal

from decimal import InvalidOperation


def layout():

    title = [
        [sg.Text("Заказ продукции", font=settings.font_h1)],
        [sg.Combo(
            [OrderCategory.POINT_PRODUCTS.value,
             OrderCategory.STOCK_PRODUCTS.value,
             OrderCategory.COUPON_PRODUCTS.value],
            default_value=OrderCategory.POINT_PRODUCTS.value,
            disabled=False,
            enable_events=True,
            expand_x=True,
            metadata=None,
            key='-SELECT_CATEGORY-'
            )]
        ]
    action = [
        [sg.Text(
             "--/--/--", visible=False, justification='r', key='-TXT_DATE-'),
         sg.Button("Получить остатки", key='-GET_STOCK-', size=(16, 1))],
        [sg.ProgressBar(
         settings.size_progresbar, style="classic", size=(18, 10), expand_x=True, key='-PROGRES-'),
         ],
        ]

    headr = []
    action_line = [
        sg.Column(title, key='-C1-', element_justification='l', expand_x=True),
        sg.Column(action, key='-C2-', element_justification='r', expand_x=True),
    ]

    result_text = [
        [sg.Text(
            "Количество позиций: ", font=settings.font_window, justification='l', pad=((5, 1), (3, 3))),
         sg.Text(
             "0 шт.", font=settings.font_window+" bold", justification='l', key='-COUNT_SCU-', pad=((0, 0), (3, 3)))],
        [sg.Text(
            "Количество выбранных товаров: ", font=settings.font_window, justification='l', pad=((5, 1), (3, 3))),
         sg.Text(
             "0 уп.", font=settings.font_window+" bold", justification='l', key='-COUNT_THING-', pad=((0, 0), (3, 3)))],
        [sg.Text(
            "Сумма выбранных товаров: ", font=settings.font_window, justification='l', pad=((5, 1), (3, 3))),
         sg.Text(
             "0 руб.", font=settings.font_window+" bold", justification='l', key='-SUM_ORDER_PRODUCT-',
             pad=((0, 0), (3, 3)))],
        [sg.Text(
            "Баллы за товар: ", font=settings.font_window, justification='l', pad=((5, 1), (3, 3))),
         sg.Text(
             "0", font=settings.font_window+" bold", justification='l', key='-BALLS_PRODUCT-',
             pad=((0, 0), (3, 3)))]
        ]

    button_section = [[sg.pin(sg.Button("<< Корректировать", size=(18, 1), visible=False, key='-CORRECT_ORDER-')),
                       sg.Button(
                           "Заказать >>",
                           size=(18, 1),
                           key='-SEND_ORDER-',
                           metadata=ButtonOrderState.get_button_order_metadata())]]

    address_section = [[
        sg.Column([
            [
                sg.Push(), sg.Text("ФИО", font=settings.font_window, justification='l'),
                sg.Input(size=(40, 1), key='-IN_FIO-')
                ],
            [
                sg.Push(), sg.Text("Телефон", font=settings.font_window, justification='l'),
                sg.Input(size=(40, 1), key='-IN_PHONE-')
                ],
            [
                sg.Push(), sg.Text("Адрес", font=settings.font_window, justification='l'),
                sg.Input(size=(40, 1), key='-IN_ADDRES-')
                ],
            [
                sg.Push(), sg.Text("Почтовый индекцс", font=settings.font_window, justification='l'),
                sg.Input(size=(40, 1), key='-IN_POST_INDEX-')
                ],
            [
                sg.Push(), sg.Text("Примечание", font=settings.font_window, justification='l'),
                sg.Input(size=(40, 1), key='-IN_NOTE-')
                ],
            ]),
        ]]

    main_content = [
        [_make_table()],
        [sg.Column(result_text, key='-C3-', element_justification='l', expand_x=True),
         sg.Column(button_section, key='-C4-', vertical_alignment='top', element_justification='r', expand_x=True)],
        [sg.pin(sg.Column(address_section, visible=False, element_justification='r', key='-ADRRES_SECTION-'))]
        ]
    fotter = []

    return [
        headr,
        action_line,
        main_content,
        fotter
    ]


def _make_table():
    head_tbale = [
            "Категория",
            "Код",
            "Название",
            "Розничная цена",
            "Складская цена",
            "Баллы",
            "Остаток",
            "Заказ"]

    return sg.Table(
        values=[[]],
        headings=head_tbale,
        header_font=settings.font_table_h,
        font=settings.font_table_d,
        # border_width=10,
        max_col_width=150,
        auto_size_columns=True,
        col_widths=(16, 6, 50, 5, 5, 5, 6, 6),
        cols_justification=('l', 'l', 'l', 'r', 'r', 'r', 'r', 'r'),
        row_height=settings.row_height_table,
        # pad=(4, 8),
        num_rows=30,
        display_row_numbers=True,
        alternating_row_color=settings.alternating_row_color,
        selected_row_colors=settings.selected_row_colors,
        enable_events=True,
        enable_click_events=True,
        expand_x=True,
        expand_y=False,
        key='-TABLE-')


def window_input_number(name_product: str, max_number: Decimal) -> Decimal:
    # TODO передтать чило введенное в заказ
    input_num = 0
    error_mesage = ""
    while True:
        input_txt = sg.popup_get_text(
            message=f'{error_mesage}{name_product}: {max_number}',
            # default_text="0",
            modal=True,
            no_titlebar=True,
            font=settings.font_window,)

        try:
            if input_txt:
                input_txt = input_txt.strip().replace(",", ".")
                input_num = Decimal(input_txt)
                if input_num > max_number:
                    input_num = max_number
                break
            else:
                break
        except InvalidOperation or ValueError:
            error_mesage = "Вводить только число\n"
            continue

    return input_num
