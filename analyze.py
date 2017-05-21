"""Takes a scan with the profile and analyzes it to score."""
import json


class ScoredTest(object):
    def __init__(self, scan):
        """
            :Takes the full scan from a dyanmo
            query of disk and loads to the object.
            :Only the scoring logic happens here not the
            assignment of grades or messaging.
        """
        self.scan = scan
        self.unknown_message = """
            This could not be evaluated in the run time.
        """

    def run(self):
        """Main map table of items to score."""
        scores = {
            "check_temp_location_supports_write":
            self.check_temp_location_supports_write
        }
        return self.make_result_dict(scores)

    def make_result_dict(self, d):
        """Create dictionary of results.

        Given the lookups dict (strings to fns),
        will return the dictionary with fns replaced by the results of
        calling them.
        """
        return {k: v() for (k, v) in d.iteritems()}

    def validate(self):
        try:
            self.scan = json.loads(self.scan)
            return True
        except:
            return False

    def check_temp_location_supports_write(self):
        """
            :Parse the json to determine persistence via warmness.
        """
        check_name = "Temp location supports write."
        modifier = 5  # TBD what the severities will be.
        fail_messaging = """
            The sandbox allows writing data to the /tmp directory.  This could
            potentially allow an attacker to persist in the environment by
            planting malicious executables to be called during subsequent
            executions.  Consider wiping the /tmp directory at the end of
            execution or disallowing execution in your environment.
        """

        success_messaging = """
            The sandbox does not allow writing data to the /tmp directory.
            This is a means of preventing persistence attacks in warm
            containers that could be called in subsequent runs.
        """

        if self.scan['tmp_rw'] is True:
            modifier = (modifier * -1)
            messaging = fail_messaging
        elif self.scan['tmp_rw'] is False:
            messaging = success_messaging
            modifier = (modifier * 1)
        else:
            messaging = self.unknown_message
            modifier = 0

        return {'check': check_name, 'score': modifier, 'message': messaging}
