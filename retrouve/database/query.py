from time import time
from retrouve.database.model import get_database_connection


class Query:
    def __init__(self, query):
        self.query = query
        self.db = get_database_connection()
        self.elapsed_time = None

    def getquery(self):
        return self.query

    def results(self):
        try:
            start_time = time()
            cursor = self.db.cursor()
            cursor.execute("SELECT url, domain, title, "
                           "ts_headline(excerpts.language, documents.body_plain, plainto_tsquery(%(query)s), 'StartSel=<mark>, StopSel=</mark>') as excerpt, "
                           "ts_rank_cd(excerpts.body, plainto_tsquery(%(query)s)) AS rank, "
                           "excerpts.language as language "
                           "FROM excerpts JOIN documents ON documents.id = excerpts.document_id "
                           "JOIN urls ON urls.id = documents.url_id "
                           "WHERE excerpts.body @@ plainto_tsquery(%(query)s) "
                           "ORDER BY rank DESC, excerpts.created_at DESC "
                           "LIMIT 30", {'query': self.getquery()})
            results = cursor.fetchall()
            self.db.commit()
            self.elapsed_time = time() - start_time
        except Exception as e:
            print("Oh noes, postgres threw an error on us")
            print(e)
            self.db.rollback()
            results = []

        cursor.close()
        return results
