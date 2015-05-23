from nose.tools import *
from retrouve.database.model import Model


def test_model_constructor():
    m = Model(foo='bar')

    assert_true('foo' in m.__dict__)
    assert_equal(m.foo, 'bar')

    m = Model(foo='bar', baz='quux', zod=1)

    assert_true('foo' in m.__dict__)
    assert_equal(m.foo, 'bar')
    assert_true('baz' in m.__dict__)
    assert_equal(m.baz, 'quux')

def test_model_dynamic_attributes():
    m = Model()
    m.foo = 'bar'

    assert_true('foo' in m.__dict__)
    assert_equal(m.foo, 'bar')

def test_model_defaults():
    m = Model()

    assert_equal(m.id, None)
