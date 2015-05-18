from urllib.parse import urlparse
from retrouve.database.model import Model
import psycopg2

class Url(Model):
    def __init__(self, url):
        self.url = url
        self.parts = urlparse(self.url)

    def insert(self):
        cur = self.db.cursor()
        p = self.parts
        try:
            cur.execute("INSERT INTO urls (url, scheme, domain, path, params, query, fragment) VALUES"
                        "(%s, %s, %s, %s, %s, %s, %s)",
                        (self.url, p.scheme, p.netloc, p.path, p.params, p.query, p.fragment))
            self.db.commit()
            cur.close()
        except psycopg2.Error as e:
            print("Postgres returned an error!")
            print(e.diag.message_primary)
            return False
        return cur.rowcount == 1

    @staticmethod
    def find(self, id):
        pass

    def domain(self):
        return self.parts.netloc

    def __str__(self):
        return self.url
