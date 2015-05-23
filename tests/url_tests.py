from nose.tools import *
from retrouve.database.model import Model
from retrouve.database.url import Url


# def test_url_from_existing_url():
#     u = Url(url='https://syntaxleiden.nl/foo')
#
#     assert_true('url' in u.__dict__)
#     assert_true('parts' in u.__dict__)
#     assert_equals(u.parts.netloc, 'syntaxleiden.nl')
#     assert_equals(u.parts.path, '/foo')
#     # assert_equals(u.parts.port, 80)
#
#
# def test_url_insert():
#     u = Url(url='https://syntaxleiden.nl/foo')
#     assert_true(u.insert())
#     assert_false(u.id is None)
#
#     ub = Url.find(u.id)
#     assert_equal(u.url, ub.url)
#     assert_equal(u.scheme, ub.scheme)

def test_default_url_parsing():
    location = 'https://syntaxleiden.nl/foo'
    u = Url(url=location)
    assert_equal(u.geturl(), location)

def test_relative_url_parsing_with_scheme():
    location = '/foo'
    u = Url(url=location, base='https://syntaxleiden.nl')
    assert_equal(u.geturl(), 'https://syntaxleiden.nl/foo')