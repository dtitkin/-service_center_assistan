import PySimpleGUI as sg

from utils.enumirate import OrderCategory

from utils.config import settings


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
            key='-SELECT_CATEGORY-'
            )]
        ]
    action = [
        [sg.Button("Получить остатки", key='-GET_STOCK-', size=(18, 1))],
        [sg.ProgressBar(
            25, style="classic", size=(18, 10), expand_x=True, key='-PROGRES-'),
         sg.Text(
             "Остатки получены --/--/--", visible=False, justification='r', key='-TXT_DATE-')
         ],
        ]

    headr = []
    action_line = [
        sg.Column(title, key='-C1-', element_justification='l', expand_x=True),
        sg.Column(action, key='-C2-', element_justification='r', expand_x=True),
    ]
    main_content = [_make_table()]
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
        max_col_width=50,
        auto_size_columns=True,
        cols_justification=('l', 'l', 'l', 'r', 'r', 'r', 'r', 'r'),
        num_rows=30,
        display_row_numbers=True,
        alternating_row_color='lightblue',
        selected_row_colors='red on yellow',
        enable_events=True,
        enable_click_events=True,
        expand_x=True,
        expand_y=False,
        key='-TABLE-')
