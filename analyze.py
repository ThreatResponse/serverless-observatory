"""Takes a scan with the profile and analyzes it to score."""
import aws
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
        self.dynamo_scans = aws.connect_dynamo(
            table_name='observatory_scans'
        )

        self.dynamo_scores = aws.connect_dynamo(
            table_name='observatory_scores'
        )

    def run(self):
        """Main map table of items to score."""
        scan_status = self.scan.get('scored', False)
        if scan_status is False:
            scores = {
                "check_temp_location_supports_write":
                self.check_temp_location_supports_write,
                "check_internet_egress":
                self.check_internet_egress
            }

            results = self.make_result_dict(scores)
            results['uuid'] = self.scan['uuid']
            # Store the score record in dynamodb
            self.__store(results)
            self.__marked_scored()

            return results
        else:
            return None

    def __store(self, scores):
        return self.dynamo_scores.put_item(
            Item=scores
        )

    def __marked_scored(self):
        return self.dynamo_scans.update_item(
            Key={
                'uuid': self.scan['uuid']
            },
            AttributeUpdates={
                'scored': {
                    'Value': True,
                    'Action': 'PUT'
                }
            }
        )

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
        points = 5  # TBD what the severities will be.
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
            modifier = (points * -1)
            messaging = fail_messaging
        elif self.scan['tmp_rw'] is False:
            messaging = success_messaging
            modifier = (points * 1)
        else:
            messaging = self.unknown_message
            modifier = 0

        return {
            'check': check_name, 'score': modifier,
            'score_possible': points, 'message': messaging
        }

    def check_internet_egress(self):
        """
            :Parse the json to determine whether we can reach arbitrary sites.
        """
        check_name = "Internet egress to world possible."
        points = 5  # TBD what the severities will be.
        fail_messaging = """
            The sandbox allows egress to the internet. A stealthy attacker
            could use this to exfiltrate data or call for other arbitrary
            payloads.
        """

        success_messaging = """
            The sandbox does not support egress to the internet making data
            exfiltration less likely but not impossible.  Exfil may still
            be possible through side channel attacks.
        """

        if self.scan['internet_egress'] is True:
            modifier = (points * -1)
            messaging = fail_messaging
        elif self.scan['internet_egress'] is False:
            messaging = success_messaging
            modifier = (points * 1)
        else:
            messaging = self.unknown_message
            modifier = 0

        return {
            'check': check_name, 'score': modifier,
            'score_possible': points, 'message': messaging
        }
