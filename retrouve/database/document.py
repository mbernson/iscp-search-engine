from retrouve.database.model import Model
from retrouve.database.url import Url
from retrouve.util import merge_dicts
from bs4 import BeautifulSoup
from retrouve.config import allowed_domains
import json


def is_allowed(url):
    return url.parts.netloc in allowed_domains or url.parts.netloc == ''


class Document(Model):
    def __init__(self, **kwargs):
        defaults = {
            'title': '',
            'body': '',
            'language': 'dutch',
            'can_index': False
        }
        args = merge_dicts(defaults, kwargs)
        super().__init__(**args)
        self.parse_html()

    def parse_html(self):
        if not self.can_index:
            return

        self.soup = BeautifulSoup(self.body)
        try:
            self.title = self.soup.title.string
        except AttributeError:
            pass

    def insert(self):
        cursor = self.db.cursor()
        cursor.execute("INSERT INTO documents (language, url_id, status_code, headers, title, body) VALUES "
                       "(%(language)s, %(url_id)s, %(status_code)s, %(headers)s, %(title)s, %(body)s) RETURNING id", self.serialize())
        self.db.commit()
        self.id = cursor.fetchone()['id']
        cursor.close()
        return self.id

    def add_urls_to_index(self):
        urls = []
        cursor = self.db.cursor()
        for link in self.soup.find_all('a'):
            url = Url(url=link.get('href'), base=self.url)
            if is_allowed(url):
                url.insert_bare(cursor)
                urls.append(url)
                print(url.geturl())

        if cursor.rowcount >= 0:
            print("Discovered %d new URL's" % cursor.rowcount)

        self.db.commit()
        cursor.close()

    def create_excerpts(self):
        pass

    def purge_docs_for_url(self, url):
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM documents WHERE url_id = %s", (url.id,))
        self.db.commit()
        cursor.close()

    def serialize(self):
        attrs = self.__dict__.copy()
        attrs['url_id'] = self.url.id
        attrs['headers'] = json.dumps(dict(self.headers))
        return attrs

    @staticmethod
    def from_response(response, url):
        if 'text/html' in response.headers['content-type']:
            doc = Document(url=url, status_code=response.status_code, headers=response.headers, body=response.text, can_index=True)
        else:
            doc = Document(url=url, status_code=response.status_code, headers=response.headers)
            doc.can_index = False

        return doc
