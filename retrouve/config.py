from retrouve.database.model import get_database_connection


def get_allowed_domains():
    """
    Get a list of the domains that are allowed to be indexed.
    Each domain is a FQDN without the scheme or slashes.
    For example: 'hsleiden.nl'
    :return: list
    """
    db = get_database_connection()
    query = "select distinct domain from urls"
    cursor = db.cursor()
    cursor.execute(query)
    db.commit()
    return [x['domain'] for x in cursor.fetchall()]
