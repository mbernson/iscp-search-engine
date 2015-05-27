from retrouve.database.model import Model


class Excerpt(Model):
    def insert_bare(self, cursor):
        if self.body is None or self.body == '':
            return False

        cursor.execute("INSERT INTO excerpts (document_id, language, tag, body)"
                       "VALUES (%(document_id)s, %(language)s, %(tag)s, to_tsvector(%(language)s, %(body)s))", self.serialize())
