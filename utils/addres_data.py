import shelve
from .config import conf_folder
from pathlib import Path


class Addres():
    # TODO whith
    def __init__(self):
        self.db = shelve.open(Path(conf_folder, 'addres'))

    def __del__(self):
        try:
            self.db.close()
        except Exception:
            pass

    @property
    def fio(self):
        return self.db.get('fio', "")

    @fio.setter
    def fio(self, value):
        self.db['fio'] = value

    @property
    def phone(self):
        return self.db.get('phone', "")

    @phone.setter
    def phone(self, value):
        self.db['phone'] = value

    @property
    def addres(self):
        return self.db.get('addres', "")

    @addres.setter
    def addres(self, value):
        self.db['addres'] = value

    @property
    def post_index(self):
        return self.db.get('post_index', "")

    @post_index.setter
    def post_index(self, value):
        self.db['post_index'] = value

    @property
    def note(self):
        return self.db.get('note', "")

    @note.setter
    def note(self, value):
        self.db['note'] = value
