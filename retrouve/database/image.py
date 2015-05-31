from retrouve.database.model import Model


class Image(Model):
    """
    Represents an image from a document, as it is stored in the database.
    """

    def insert_bare(self, cursor):
        """
        Perform a SQL insert of this image using a database cursor.
        :param cursor: :class:`cursor` object
        """
        cursor.execute("INSERT INTO images (document_id, url, alt)"
                       "VALUES (%(document_id)s, %(url)s, %(alt)s)", self.serialize())
