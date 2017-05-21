import analyze


def test_analyze_object():
    f = open('tests/sample.json', 'r')
    f = f.read()
    a = analyze.ScoredTest(f)
    assert a is not None


def test_validate_function():
    f = open('tests/sample.json', 'r')
    f = f.read()
    a = analyze.ScoredTest(f)
    res = a.validate()
    assert res is True


def test_validate_function_fails():
    f = "123987sdfjbcvsd7ah 98h bjnp\\\\21&@$^&^#$(@$&!@#)"
    a = analyze.ScoredTest(f)
    res = a.validate()
    assert res is False


def test_reporting_temp_rw():
    f = "{\"tmp_rw\": true}"
    a = analyze.ScoredTest(f)
    a.validate()
    res = a.check_temp_location_supports_write()
    assert res is not None
    assert res['score'] is -5


def test_full_eval():
    f = open('tests/sample.json', 'r')
    f = f.read()
    a = analyze.ScoredTest(f)
    a.validate()
    res = a.run()
    assert 'check_temp_location_supports_write' in res.keys()
    assert 'score' in res['check_temp_location_supports_write'].keys()
    assert 'score' in res['check_temp_location_supports_write'].keys()
