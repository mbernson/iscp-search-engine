from retrouve.database.model import Model

class Excerpt(Model):
    """
    Represents a snippet of text from a document, as it is stored in the database.
    """

    def insert_bare(self, cursor):
        """
        Perform a SQL insert of this excerpt using a database cursor.
        :param cursor: :class:`cursor` object
        """
        if self.body is None or self.body == '':
            return False

        cursor.execute("INSERT INTO excerpts (document_id, language, tag, body)"
                       "VALUES (%(document_id)s, %(language)s, %(tag)s, to_tsvector(%(language)s, %(body)s))", self.serialize())
