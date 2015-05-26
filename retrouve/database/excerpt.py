import psycopg2
import psycopg2.extras
from retrouve.database.model import Model, get_database_connection


class Excerpt(Model):
    def insert_bare(self, cursor):
        # TODO: Add importance
        cursor.execute("INSERT INTO excerpts (document_id, language, tag, body)"
                       "VALUES (%(document_id)s, %(language)s, %(tag)s, %(body)s)", self.serialize())
        print(cursor.statusmessage)

