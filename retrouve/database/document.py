from retrouve.database.model import Model
from retrouve.database.url import Url
from retrouve.database.excerpt import Excerpt
from retrouve.database.image import Image
from retrouve.util import merge_dicts
from bs4 import BeautifulSoup
from retrouve.config import get_allowed_domains
import json


class Document(Model):
    """
    Represents a single web page as it was fetched at a certain point in time.
    """

    def __init__(self, **kwargs):
        """
        Initialize the document with default parameters.
        :param kwargs:
        """
        defaults = {
            'title': '',
            'body': '',
            'body_plain': '',
            'language': 'dutch',
            # can_index prevents a document from being indexed if it's not HTML
            'can_index': False
        }
        args = merge_dicts(defaults, kwargs)
        super().__init__(**args)
        self.__parse_html()

    def __parse_html(self):
        if not self.can_index:
            return

        self.soup = BeautifulSoup(self.body)
        self.body_plain = self.soup.get_text()

        try:
            self.title = self.soup.title.string
        except AttributeError:
            pass

    def insert(self):
        """
        Save the document to the database.
        :return: integer
        """
        cursor = self.db.cursor()
        cursor.execute("INSERT INTO documents (language, url_id, status_code, headers, title, body, body_plain) VALUES "
                       "(%(language)s, %(url_id)s, %(status_code)s, %(headers)s, %(title)s, %(body)s, %(body_plain)s) RETURNING id", self.serialize())
        self.db.commit()
        self.id = cursor.fetchone()['id']
        cursor.close()
        print("Saved new document with id %s" % self.id)
        return self.id

    def discover_urls(self):
        """
        Discover URL's in the document and save them in the database.
        """
        allowed_domains = get_allowed_domains()

        def is_allowed(u):
            return u.domain() in allowed_domains or u.domain() == ''

        urls = []
        cursor = self.db.cursor()
        for link in self.soup.find_all('a'):
            url = Url(url=link.get('href'), base=self.url)
            if is_allowed(url):
                url.insert_bare(cursor)
                urls.append(url)

        self.db.commit()
        cursor.close()

    """The tags from which excerpts can be extracted"""
    tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']

    def discover_excerpts(self):
        """
        Discover excerpts (fragments of text) in the document and save them in the database.
        """
        cursor = self.db.cursor()
        if self.exists():
            cursor.execute("DELETE FROM excerpts WHERE document_id = %s", (self.id,))

        for tag in self.tags:
            for element in self.soup.find_all(tag):
                excerpt = Excerpt(body=element.text, tag=tag, language=self.language, document_id=self.id)
                excerpt.insert_bare(cursor)

        self.db.commit()
        cursor.close()

    def discover_images(self):
        """
        Discover images in the document and save them in the database.
        """
        cursor = self.db.cursor()
        if not self.is_new():
            cursor.execute("DELETE FROM images WHERE document_id = %s", (self.id,))

        for image in self.soup.find_all('img'):
            image = Image(url=image.get('src'), alt=image.get('alt'), document_id=self.id)
            image.insert_bare(cursor)

        self.db.commit()
        cursor.close()

    def purge_docs_for_url(self, url):
        """
        Remove existing documents for this URL from the database.
        :param url: A :class:`Url` object
        """
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM documents WHERE url_id = %s", (url.id,))
        self.db.commit()
        cursor.close()

    def serialize(self):
        """
        Add the url ID and json header to the serialized dictionary.
        :return: dict
        """
        attrs = self.__dict__.copy()
        attrs['url_id'] = self.url.id
        attrs['headers'] = json.dumps(dict(self.headers))
        return attrs

    @staticmethod
    def from_response(response, url):
        """
        Construct a new document based on a response and URL.
        :param response: An HTTP response, :class:`requests.Response`
        :param url: A :class:`Url` object
        :return: :class:`Document` object
        """
        if 'text/html' in response.headers['content-type']:
            doc = Document(url=url, status_code=response.status_code, headers=response.headers, body=response.text, can_index=True)
        else:
            doc = Document(url=url, status_code=response.status_code, headers=response.headers)
            doc.can_index = False

        return doc
