from retrouve.database.model import Model


class Query(Model):
    def __init__(self, query):
        self.query = query

    def getquery(self):
        return self.query

    def results(self):
        try:
            cursor = self.db.cursor()
            cursor.execute("SELECT url, domain, title, "
                           "ts_headline(excerpts.language, excerpts.body, plainto_tsquery(%(query)s), 'StartSel=<mark>, StopSel=</mark>') as excerpt, "
                           "ts_rank_cd(to_tsvector(excerpts.language, excerpts.body), plainto_tsquery(%(query)s)) AS rank, "
                           "excerpts.language as language "
                           "FROM excerpts JOIN documents ON documents.id = excerpts.document_id "
                           "JOIN urls ON urls.id = documents.url_id "
                           "WHERE excerpts.body @@ plainto_tsquery(%(query)s) "
                           "AND excerpts.body != '' "
                           "ORDER BY rank DESC, excerpts.created_at DESC "
                           "LIMIT 30", {'query': self.getquery()})
            results = cursor.fetchall()
            self.db.commit()
        except Exception as e:
            print("Oh noes, postgres threw an error on us")
            print(e)
            self.db.rollback()
            results = []

        cursor.close()
        return results
