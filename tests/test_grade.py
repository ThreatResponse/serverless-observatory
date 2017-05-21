import grade


def test_grade_object():
    good_score = {
                'foo_check': {
                    'check_name': 'foo',
                    'score': 5,
                    'message': 'you are secure'
                },
                'bar_check': {
                    'check_name': 'foo',
                    'score': 60,
                    'message': 'you are secure'
                }
              }

    g = grade.Grade()
    this_grade = g.get_grade(good_score)
    assert g is not None
    assert this_grade['score'] == 65
    assert this_grade['grade'] == 'B-'


def test_grade_rounding():
    good_score = {
                'foo_check': {
                    'check_name': 'foo',
                    'score': 3,
                    'message': 'you are secure'
                },
                'bar_check': {
                    'check_name': 'foo',
                    'score': 60,
                    'message': 'you are secure'
                }
              }

    g = grade.Grade()
    this_grade = g.get_grade(good_score)
    assert g is not None
    # 63 is rounded up to 65 in this case
    assert this_grade['score'] == 65
    assert this_grade['grade'] == 'B-'
