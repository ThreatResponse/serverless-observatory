import os
import sys
import random
from faker import Factory


sys.path.append(os.getcwd())

import user
fake = Factory.create()

MOCK_PROFILE = {
    'user_id': 'foo',
    'email': 'bar'
}

MOCK_NEW_USER = {
    'user_id': fake.ean8(),
    'email': fake.free_email()
}


def test_object_init():
    u = user.User(MOCK_PROFILE)
    result = u.find_or_create_by()
    assert result is not None
    assert u is not None


def test_user_creation():
    u = user.User(MOCK_NEW_USER)
    result = u.find_or_create_by()
    assert result is not None
    assert u is not None


def test_api_key_rotation():
    u = user.User(MOCK_NEW_USER)
    result = u.find_or_create_by()
    old_api_key = result['api_key']
    u.rotate_api_key()
    new_result = u.find_or_create_by()
    new_api_key = new_result['api_key']
    assert old_api_key is not new_api_key
