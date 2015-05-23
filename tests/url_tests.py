from nose.tools import *
from retrouve.database.model import Model
from retrouve.database.url import Url


def test_url_from_existing_url():
    u = Url.from_url('https://syntaxleiden.nl/foo')

    assert_true('url' in u.__dict__)
    assert_true('parts' in u.__dict__)
    assert_equals(u.parts.netloc, 'syntaxleiden.nl')
    assert_equals(u.parts.path, '/foo')
    # assert_equals(u.parts.port, 80)

def test_url_insert():
    u = Url.from_url('https://syntaxleiden.nl/foo')
    assert_true(u.insert())
    assert_false(u.id is None)

    ub = Url.find(u.id)
    assert_equal(u.url, ub.url)
    assert_equal(u.scheme, ub.scheme)

