import PySimpleGUI as sg

from datetime import datetime

from time import sleep


def handle(window: sg.Window, event, value):
    if event == '-GET_STOCK-':
        window['-TXT_DATE-'].update(visible=False)
        window['-PROGRES-'].update(visible=True)
        for i in range(0, 50):
            sleep(0.1)
            now_value = 25/50*i
            window['-PROGRES-'].update(current_count=now_value)
        window['-PROGRES-'].update(visible=False)
        window['-TXT_DATE-'].update(
            value=datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
            visible=True)
