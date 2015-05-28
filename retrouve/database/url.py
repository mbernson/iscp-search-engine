from urllib.parse import urlparse, urlunparse
from retrouve.database.model import Model, get_database_connection
import psycopg2

db = get_database_connection()


class Url(Model):
    """
    Represents a URL as it is stored in the database.
    """

    def __init__(self, **kwargs):
        """
        Construct the URL, and parse the URL into parts right away.
        :param kwargs:
        """
        super().__init__(**kwargs)
        if hasattr(self, 'url'):
            self.parse_url()

    def parse_url(self):
        """
        Parse the URL into its components, using a base URL when possible.
        The URL components are stored in the internal __parts property.
        """
        self.__parts = urlparse(self.url)
        if hasattr(self, 'base'):
            if isinstance(self.base, str):
                self.base = urlparse(self.base)
            elif isinstance(self.base, Url):
                self.base = self.base.__parts

    def geturl(self):
        """
        Get the fully-qualified URL for this URL object.
        :return: string
        """
        return urlunparse(self.getparts())

    def getparts(self):
        if hasattr(self, 'base'):
            p = self.__parts
            b = self.base
            # Please, let there be a better way to do this
            return p.scheme or b.scheme, p.netloc or b.netloc, p.path or b.path, p.params or b.params, p.query or b.query, p.fragment or b.fragment
        else:
            return self.__parts

    def insert(self):
        """
        Persist the URL to the database as a new row.
        :return:
        """
        cursor = self.db.cursor()
        try:
            self.insert_bare(cursor)
            self.db.commit()
            cursor.close()
            return cursor.rowcount == 1
        except psycopg2.Error as e:
            print(e)
            self.db.rollback()
            cursor.close()
            return False

    def insert_bare(self, cursor):
        url = self.geturl()
        parts = self.getparts()

        # Ensure this URL doesn't exist yet
        cursor.execute("SELECT id FROM urls WHERE scheme = %s AND domain = %s AND path = %s AND params = %s AND query = %s LIMIT 1", parts[0:5])
        if cursor.rowcount > 0:
            return False

        cursor.execute("INSERT INTO urls (url, scheme, domain, path, params, query, fragment)"
                       "VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",
                       (url,) + parts)
        result = cursor.fetchone()
        self.id = result['id']
        print("Saved new URL %s with id %s" % (url, self.id))
        return True

    @staticmethod
    def find(url_id):
        cursor = db.cursor()
        cursor.execute("SELECT * FROM urls WHERE id = %s LIMIT 1", (url_id,))

        result = cursor.fetchone()
        db.commit()
        cursor.close()
        if result is None:
            return None

        url = Url(**result)

        return url

    def destroy(self):
        """
        Remove this URL from the database.
        :return: boolean
        """
        if self.is_new():
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
        """
        Return the domain name of this URL.
        :return:
        """
        return self.__parts.netloc

    def __str__(self):
        return self.geturl()
