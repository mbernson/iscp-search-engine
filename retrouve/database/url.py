import psycopg2
from urllib.parse import urlparse

class Model(object):
    db = psycopg2.connect(database='search_engine', user='search_engine', password='search_engine')

class Url(Model):
    def __init__(self, url):
        self.url = url
        self.parts = urlparse(self.url)

    def insert(self):
        cur = self.db.cursor()
        p = self.parts
        cur.execute("INSERT INTO urls (url, scheme, domain, path, params, query, fragment) VALUES"
                    "(%s, %s, %s, %s, %s, %s, %s)",
                    (self.url, p.scheme, p.netloc, p.path, p.params, p.query, p.fragment))
        self.db.commit()
        cur.close()
        return cur.rowcount == 1

    def domain(self):
        return self.parts.netloc

    def __str__(self):
        return self.url