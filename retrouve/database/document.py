from retrouve.database.model import Model
from retrouve.database.url import Url
from retrouve.database.excerpt import Excerpt
from retrouve.database.image import Image
from retrouve.util import merge_dicts
from bs4 import BeautifulSoup
from retrouve.config import get_allowed_domains
import json


class Document(Model):
    def __init__(self, **kwargs):
        """
        Initialize the document with default parameters.
        :param kwargs:
        """
        defaults = {
            'title': '',
            'body': '',
            'language': 'dutch',
            # can_index prevents a document from being indexed if it's not HTML
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
        print("Saved new document with id %s" % self.id)
        return self.id

    def add_urls_to_index(self):
        allowed_domains = get_allowed_domains()

        def is_allowed(u):
            return u.parts.netloc in allowed_domains or u.parts.netloc == ''

        urls = []
        cursor = self.db.cursor()
        for link in self.soup.find_all('a'):
            url = Url(url=link.get('href'), base=self.url)
            if is_allowed(url):
                url.insert_bare(cursor)
                urls.append(url)
                print(url.geturl())

        self.db.commit()
        cursor.close()

    tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']

    def create_excerpts(self):
        cursor = self.db.cursor()
        if self.exists():
            cursor.execute("DELETE FROM excerpts WHERE document_id = %s", (self.id,))

        for tag in self.tags:
            for element in self.soup.find_all(tag):
                excerpt = Excerpt(body=element.text, tag=tag, language=self.language, document_id=self.id)
                excerpt.insert_bare(cursor)

        self.db.commit()
        cursor.close()

    def save_images(self):
        cursor = self.db.cursor()
        if not self.isnew():
            cursor.execute("DELETE FROM images WHERE document_id = %s", (self.id,))

        for image in self.soup.find_all('img'):
            image = Image(url=image.get('src'), alt=image.get('alt'), document_id=self.id)
            image.insert_bare(cursor)

        self.db.commit()
        cursor.close()

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
