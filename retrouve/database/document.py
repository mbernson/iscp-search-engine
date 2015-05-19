from retrouve.database.model import Model
from retrouve.database.url import Url

class Document(Model):
    def __init__(self):
        pass

    @staticmethod
    def from_url(url):
        pass

    @staticmethod
    def from_response(response):
        self.status = response.status_code
        self.headers = response.headers
        self.body = response.text
        # self.title = response.title

    def insert(self):
        pass
