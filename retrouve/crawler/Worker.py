from .. import config

from urllib.parse import urlparse

class Worker:
    def __init__(self):
        config.db.database
        print('Worker')

    def dummy(self):
        u = urlparse('https://fotos.syntaxleiden.nl/index.php?/category/11/start-30')
        print(u.host)