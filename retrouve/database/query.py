from retrouve.database.model import Model

class Query(Model):
    def __init__(self, query):
        self.query = query

    def getquery(self):
        return self.query

    def results(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT url, domain, title, excerpts.body as excerpt "
                       "FROM excerpts JOIN documents ON documents.id = excerpts.document_id JOIN urls ON urls.id = documents.url_id "
                       "WHERE excerpts.body @@ to_tsquery(%(query)s) "
                       "AND excerpts.body != '' "
                       "ORDER BY excerpts.created_at DESC "
                       "LIMIT 30", {'query':self.getquery()})
        results = cursor.fetchall()
        self.db.commit()
        cursor.close()
        return results

