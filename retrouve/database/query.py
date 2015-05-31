from time import time
from retrouve.database.model import get_database_connection


class Query:
    """
    Represents a single search query that is performed against the database.
    """

    def __init__(self, query):
        """
        Construct with a search query.
        :param query: string, the search query to use.
        """
        self.query = query
        self.db = get_database_connection()
        self.elapsed_time = None

    def getquery(self):
        """Return the search query"""
        return self.query

    def results(self, amount=50):
        """
        Return results for the query.
        :return: list
        """
        try:
            params = {
                'query': self.getquery(),
                'amount': amount
            }
            start_time = time()
            cursor = self.db.cursor()
            cursor.execute("SELECT DISTINCT url, domain, title, "
                           "ts_headline(excerpts.language, documents.body_plain, plainto_tsquery(%(query)s), 'StartSel=<mark>, StopSel=</mark>') as excerpt, "
                           "ts_rank_cd(excerpts.body, plainto_tsquery(%(query)s)) AS rank, "
                           "excerpts.language as language "
                           "FROM excerpts JOIN documents ON documents.id = excerpts.document_id "
                           "JOIN urls ON urls.id = documents.url_id "
                           "WHERE excerpts.body @@ plainto_tsquery(%(query)s) "
                           "ORDER BY rank DESC "
                           "LIMIT %(amount)s", params)
            results = cursor.fetchall()
            self.db.commit()
            self.elapsed_time = time() - start_time
        except Exception as e:
            print(e)
            self.db.rollback()
            results = []

        cursor.close()
        return results
