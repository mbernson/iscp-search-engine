import psycopg2
import psycopg2.extras
import os

def get_database_connection():
    return psycopg2.connect(host=os.environ.get('DB_HOST'), database=os.environ.get('DB_DATABASE'),
                            user=os.environ.get('DB_USERNAME'), password=os.environ.get('DB_PASSWORD'),
                            cursor_factory=psycopg2.extras.RealDictCursor)
    # Make the connection return dictionaries instead of tuples

class Model(object):
    db = get_database_connection()

    def __init__(self, **kwargs):
        self.__dict__ = kwargs
        if not hasattr(self, 'id'):
            self.id = None
