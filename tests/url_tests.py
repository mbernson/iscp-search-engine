from nose.tools import *
from retrouve.database.url import Url


def test_default_url_parsing():
    location = 'https://syntaxleiden.nl/foo'
    u = Url(url=location)
    assert_equal(u.geturl(), location)

def test_relative_url_parsing_with_scheme():
    location = '/foo'
    u = Url(url=location, base='https://syntaxleiden.nl')
    assert_equal(u.geturl(), 'https://syntaxleiden.nl/foo')