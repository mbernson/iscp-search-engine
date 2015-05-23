from urllib.parse import urlparse
from retrouve.database.model import Model, get_database_connection
import psycopg2

db = get_database_connection()


class Url(Model):
    def insert(self):
        cur = self.db.cursor()
        try:
            self.insert_bare(cur)
            self.db.commit()
            self.id = cur.lastrowid
            cur.close()
            print("Saved url for domain %s" % self.parts.netloc)
            return cur.rowcount == 1
        except psycopg2.Error as e:
            print(e)
            self.db.rollback()
            cur.close()
            return False

    def insert_bare(self, cursor):
        p = self.parts
        cursor.execute("INSERT INTO urls (url, scheme, domain, path, params, query, fragment) VALUES"
                       "(%s, %s, %s, %s, %s, %s, %s)",
                       (self.url, p.scheme, p.netloc, p.path, p.params, p.query, p.fragment))

    @staticmethod
    def from_url(url):
        u = Url(url=url)
        if url is not None:
            u.parts = urlparse(url)
        return u

    @staticmethod
    def find(url_id):
        cur = db.cursor()
        cur.execute("SELECT * FROM urls WHERE id = %s LIMIT 1", (url_id,))

        result = cur.fetchone()
        cur.close()
        if result is None:
            return None

        url = Url()
        url.__dict__ = result

        return url

    def destroy(self):
        if self.id is None:
            return False
        cur = self.db.cursor()
        try:
            cur.execute("DELETE FROM urls WHERE id = %s", (self.id,))
            self.db.commit()
            cur.close()
            return cur.rowcount == 1
        except psycopg2.Error as e:
            print(e)
        return False

    def domain(self):
        return self.parts.netloc

    def __str__(self):
        return self.url
