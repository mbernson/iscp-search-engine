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

    def results(self, offset=0, amount=50):
        """
        Return results for the query.
        :return: list
        """
        cursor = self.db.cursor()
        try:
            params = {
                'query': self.getquery(),
                'offset': offset,
                'amount': amount
            }
            start_time = time()
            cursor.execute("SELECT DISTINCT url, domain, title, "
                           "ts_headline(excerpts.language, documents.body_plain, plainto_tsquery(%(query)s), 'StartSel=<mark>, StopSel=</mark>') as excerpt, "
                           "ts_rank_cd(excerpts.body, plainto_tsquery(%(query)s)) AS rank, excerpts.language as language "
                           "FROM excerpts, documents, urls "
                           "WHERE excerpts.body @@ plainto_tsquery(%(query)s) "
                           "AND documents.id = excerpts.document_id "
                           "AND urls.id = documents.url_id "
                           "ORDER BY rank DESC "
                           "LIMIT %(amount)s "
                           "OFFSET %(offset)s", params)
            results = cursor.fetchall()
            self.db.commit()
            self.elapsed_time = time() - start_time
        except Exception as e:
            print(e)
            self.db.rollback()
            results = []

        cursor.close()
        return results

    def count(self):
        cursor = self.db.cursor()
        cursor.execute("select count(*) amount from excerpts, documents WHERE excerpts.body @@ plainto_tsquery(%s) "
                       "and documents.id = excerpts.document_id", (self.getquery(),))
        result = cursor.fetchone()
        return result['amount']
