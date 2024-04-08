from pathlib import Path
import configparser

_conf_folder = Path(__file__).parent.parent / "conf"


class _Setiings():
    def __init__(self):
        config = configparser.ConfigParser()
        config.read(Path(_conf_folder, 'settings.ini'))

        self.login: str = config['authorization']['login']
        self.password: str = config['authorization']['password']

        self.implicitly_wait: int = int(config['wait_time']['implicitly_wait'])
        self.until_wait: int = int(config['wait_time']['until_wait'])

        self.login_uri: str = config['uri']['login_uri']

        self.main_themes: str = config['front']['main_themes']
        self.font_window: str = config['front']['font_window']
        self.font_h1: str = config['front']['font_h1']
        self.font_table_h: str = config['front']['font_table_h']
        self.font_table_d: str = config['front']['font_table_d']
        self.row_height_table: int = int(config['front']['row_height_table'])

        self.alternating_row_color: str = config['front']['alternating_row_color']
        self.selected_row_colors: str = config['front']['selected_row_colors']
        self.order_row_colors: str = config['front']['order_row_colors']

        self.size_progresbar = 25

        self.debug: bool = True if config['debug']['debug'] == 'True' else False


settings = _Setiings()
