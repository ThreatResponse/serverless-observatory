"""Grading logic modeled after April King's Mozilla Web Observatory."""
from __future__ import division


class Grade(object):
    def __init__(self):
        self.grade_chart = {
            100: 'A+',
            95: 'A',
            90: 'A',
            85: 'A-',
            80: 'B+',
            75: 'B',
            70: 'B',
            65: 'B-',
            60: 'C+',
            55: 'C',
            50: 'C',
            45: 'C-',
            40: 'D+',
            35: 'D',
            30: 'D',
            25: 'D-',
            20: 'F',
            15: 'F',
            10: 'F',
            5: 'F',
            0: 'F'
        }

    def get_grade(self, scored_test):
        total_score = self._total_score(scored_test)

        # Round up score to the nearest multiplier of 5
        total_score = int(round(total_score / 5.0) * 5.0)

        # Score against the above grade chart
        grade = self.grade_chart[total_score]

        # Return
        return {'score': total_score, 'grade': grade}

    def _total_score(self, scored_test):
        """Returns total score as a percentage."""
        score = 0
        possible_points = 0

        for k, v in scored_test.iteritems():
            score = score + v['score']
            possible_points = possible_points + v['score_possible']


        percentage_complete = (
            int(
                round(
                    float(int(score) / int(possible_points) * 100)
                )
            )
        )

        return percentage_complete
