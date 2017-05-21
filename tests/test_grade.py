import grade


def test_grade_object():
    good_score = {
                'foo_check': {
                    'check_name': 'foo',
                    'score': 5,
                    'message': 'you are secure',
                    'score_possible': 5
                },
                'bar_check': {
                    'check_name': 'foo',
                    'score': 60,
                    'message': 'you are secure',
                    'score_possible': 60
                }
              }

    g = grade.Grade()
    this_grade = g.get_grade(good_score)
    assert g is not None
    assert this_grade['score'] == 100
    assert this_grade['grade'] == 'A+'


def test_grade_rounding():
    good_score = {
                'foo_check': {
                    'check_name': 'foo',
                    'score': 5,
                    'message': 'you are secure',
                    'score_possible': 5
                },
                'bar_check': {
                    'check_name': 'foo',
                    'score': 25,
                    'message': 'you are secure',
                    'score_possible': 60
                }
              }

    g = grade.Grade()
    this_grade = g.get_grade(good_score)
    print this_grade
    assert g is not None
    # 63 is rounded up to 65 in this case
    assert this_grade['score'] == 45
    assert this_grade['grade'] == 'C-'
