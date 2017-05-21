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

MOCK_SCAN = {
    "env": {
        "LANG": "en_US.UTF-8",
        "AWS_DEFAULT_REGION": "eu-central-1",
        "AWS_LAMBDA_FUNCTION_MEMORY_SIZE": "128",
        "AWS_LAMBDA_FUNCTION_NAME": "scheduled-serverless-profiler",
        "AWS_SECRET_ACCESS_KEY": "3DLhCkBAtlZR",
        "AWS_LAMBDA_FUNCTION_VERSION": "$LATEST",
        "PYTHONPATH": "/var/runtime",
        "AWS_LAMBDA_LOG_GROUP_NAME": "/aws/lambda/scheduled-profiler",
        "AWS_REGION": "eu-central-1",
        "AWS_SESSION_TOKEN": "FQoDYXdzEH0a",
        "LAMBDA_TASK_ROOT": "/var/task",
        "AWS_EXECUTION_ENV": "AWS_Lambda_python2.7",
        "AWS_SECURITY_TOKEN": "FQoDYXdzEH0a",
        "LAMBDA_RUNTIME_DIR": "/var/runtime",
        "AWS_LAMBDA_LOG_STREAM_NAME": "2017/03/11/[$LATEST]d5e2ca93",
        "AWS_ACCESS_KEY_ID": "ASIAJPDEBYZC",
        "PATH": "/usr/local/bin:/usr/bin/:/bin"
    }
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


def test_profile_storage():
    u = user.User(MOCK_NEW_USER)
    result = u.find_or_create_by()
    p = api.Profiler(result['api_key'])
    result = p.store_profile(MOCK_SCAN)
    u.destroy()
    assert p is not None
    assert p.authenticated is True
    assert result is not None
    p.destroy_profile(result)
