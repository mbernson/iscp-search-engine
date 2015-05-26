import psycopg2
import psycopg2.extras
from retrouve.database.model import Model, get_database_connection


class Image(Model):
    def insert_bare(self, cursor):
        cursor.execute("INSERT INTO images (document_id, url, alt)"
                       "VALUES (%(document_id)s, %(url)s, %(alt)s)", self.serialize())
        print(cursor.statusmessage)

