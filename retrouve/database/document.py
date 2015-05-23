from retrouve.database.model import Model
from retrouve.database.url import Url
from retrouve.util import merge_dicts
from bs4 import BeautifulSoup
import json

class Document(Model):
    def __init__(self, **kwargs):
        defaults = {
            'title': '',
            'language': 'dutch'
        }
        args = merge_dicts(defaults, kwargs)
        super().__init__(**args)
        self.soup = None

    def parse(self):
        self.soup = BeautifulSoup(self.body)

    def insert(self):
        cursor = self.db.cursor()
        attrs = self.__dict__.copy()
        attrs['url_id'] = self.url.id
        attrs['headers'] = json.dumps(dict(self.headers))
        cursor.execute("INSERT INTO documents (language, url_id, status_code, headers, title, body) VALUES "
                       "(%(language)s, %(url_id)s, %(status_code)s, %(headers)s, %(title)s, %(body)s) RETURNING id", attrs)
        self.db.commit()
        id = cursor.fetchone()['id']
        cursor.close()
        return id

    def add_urls_to_index(self):
        if self.soup is None:
            self.parse()

        print("Detecting new URLs")

        cursor = self.db.cursor()
        for link in self.soup.find_all('a'):
            url = Url(url=link.get('href'), base=self.url)

            if url.parts.netloc == 'syntaxleiden.nl' or url.parts.netloc == '':
                url.insert_bare(cursor)
                print("Inserting URL: %s" % url)
            else:
                print("Skipping URL: %s" % url)

        self.db.commit()
        rows = cursor.rowcount
        print("Inserted %s new URLs" % rows)
        cursor.close()

    def create_excerpts(self):
        print("Creating excerpts")
        if self.soup is None:
            self.parse()

        pass

    def detect_language(self):
        # Do smart things to detect the page's language here
        pass

    @staticmethod
    def from_response(response, url):
        doc = Document(url=url, status_code=response.status_code, headers=response.headers, body=response.text)
        doc.detect_language()
        return doc
