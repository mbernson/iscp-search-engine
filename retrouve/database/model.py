import psycopg2
import psycopg2.extras
import os


def get_database_connection():
    """
    Acquire a database connection from the environment configuration.
    :rtype : psycopg2.connection
    """
    # Make the connection return dictionaries instead of tuples
    cursor_factory = psycopg2.extras.RealDictCursor
    return psycopg2.connect(host=os.environ.get('DB_HOST'), database=os.environ.get('DB_DATABASE'),
                            user=os.environ.get('DB_USERNAME'), password=os.environ.get('DB_PASSWORD'),
                            cursor_factory=cursor_factory)


class Model(object):
    """
    Base class for data objects.
    A model can easily be serialized to a dictionary and back.
    """

    """Shared connection to the database"""
    db = get_database_connection()

    def __init__(self, **kwargs):
        """Construct a model with a set of properties."""
        self.__dict__ = kwargs
        if not hasattr(self, 'id'):
            self.id = None

    def serialize(self):
        """
        Return a dictionary containing the model's attributes.
        :return: dict
        """
        return self.__dict__.copy()

    def is_new(self):
        """
        Return true if the model has not been persisted to storage.
        :return: boolean
        """
        return not self.exists()

    def exists(self):
        """
        Return true if the model has been persisted to storage.
        :return: boolean
        """
        return hasattr(self, 'id') and self.id is not None
