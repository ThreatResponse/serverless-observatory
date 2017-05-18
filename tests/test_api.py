import os
import sys
from faker import Factory


sys.path.append(os.getcwd())

import api
import user
fake = Factory.create()

MOCK_NEW_USER = {
    'user_id': '3141592654',
    'email': 'foo@bar.com'
}


def test_object_init():
    a = api.APIKey('123567890')
    assert a is not None


def test_api_key_location():
    u = user.User(MOCK_NEW_USER)
    result = u.find_or_create_by()
    a = api.APIKey(result['api_key'])
    search_operation = a.locate_user()
    u.destroy()
    assert search_operation['api_key'] is not None
    assert search_operation['user_id'] == MOCK_NEW_USER['user_id']
    assert search_operation['email'] == MOCK_NEW_USER['email']
    assert search_operation['disabled'] is False


def test_profile_object():
    u = user.User(MOCK_NEW_USER)
    result = u.find_or_create_by()
    p = api.Profiler(result['api_key'])
    u.destroy()
    assert p is not None
    assert p.authenticated is True
