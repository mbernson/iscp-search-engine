from urllib.parse import urlparse, urlunparse
from retrouve.database.model import Model, get_database_connection
import psycopg2

db = get_database_connection()


class Url(Model):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if hasattr(self, 'url'):
            self.parse()

    def parse(self):
        self.parts = urlparse(self.url)
        if hasattr(self, 'base'):
            if isinstance(self.base, str):
                self.base = urlparse(self.base)
            elif isinstance(self.base, Url):
                self.base = self.base.parts

    def geturl(self):
        if not hasattr(self, 'base'):
            return self.parts.geturl()
        else:
            return urlunparse(self.merge_with_base())

    def merge_with_base(self):
        p = self.parts
        b = self.base
        # Please, let there be a better way to do this
        return p.scheme or b.scheme, p.netloc or b.netloc, p.path or b.path, p.params or b.params, p.query or b.query, p.fragment or b.fragment

    def insert(self):
        cursor = self.db.cursor()
        try:
            self.insert_bare(cursor)
            self.db.commit()
            cursor.close()
            print("Saved url for domain %s" % self.parts.netloc)
            return cursor.rowcount == 1
        except psycopg2.Error as e:
            print(e)
            self.db.rollback()
            cursor.close()
            return False

    def insert_bare(self, cursor):
        cursor.execute("INSERT INTO urls (url, scheme, domain, path, params, query, fragment) VALUES"
                       "(%s, %s, %s, %s, %s, %s, %s) RETURNING id",
                       (self.geturl(),) + self.merge_with_base())
        self.id = cursor.fetchone()['id']

    @staticmethod
    def find(url_id):
        cursor = db.cursor()
        cursor.execute("SELECT * FROM urls WHERE id = %s LIMIT 1", (url_id,))

        result = cursor.fetchone()
        cursor.close()
        if result is None:
            return None

        url = Url()
        url.__dict__ = result
        url.parse()

        return url

    def destroy(self):
        if self.id is None:
            return False
        cursor = self.db.cursor()
        try:
            cursor.execute("DELETE FROM urls WHERE id = %s", (self.id,))
            self.db.commit()
            cursor.close()
            return cursor.rowcount == 1
        except psycopg2.Error as e:
            print(e)
        return False

    def domain(self):
        return self.parts.netloc

    def __str__(self):
        return self.geturl()
