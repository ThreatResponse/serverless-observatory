""" Governs crud operations around users and data. """
import random
import aws

from boto3.dynamodb.conditions import Key
from hashids import Hashids


class Scan(object):
    """Return all of the scans and scoring statuses."""
    def __init__(self, user):
        self.user = user
        self.dynamo_scans = aws.connect_dynamo(
            table_name='observatory_scans'
        )
        self.dynamo_scores = aws.connect_dynamo(
            table_name='observatory_scores'
        )

    def find_scans_by_uid(self):
        fe = Key('user_id').eq(self.user.user_id)

        response = self.dynamo_scans.scan(
            IndexName='user_id-index',
            FilterExpression=fe,
            Select='ALL_ATTRIBUTES'
        )

        scans = []
        for i in response['Items']:
            scans.append(i)

        return scans

    def find_scan_by_key(self, uuid):
        response = self.dynamo_scans.get_item(
            Key={
                'uuid': uuid
            }
        )
        return response['Item']

    def find_score_by_key(self, uuid):
        response = self.dynamo_scores.get_item(
            Key={
                'uuid': uuid
            }
        )
        return response['Item']

    def add_friendly_timestamp(self, scan):
        pass


class User(object):

    def __init__(self, userinfo):
        self.user_id = userinfo['user_id']
        self.email = userinfo['email']
        self.name = userinfo['name']
        self.dynamo = aws.connect_dynamo(table_name='observatory_users')

    def scans(self):
        return Scan(self).find_scans_by_uid()

    def api_key(self):
        """Return the primary api key for a user."""
        return self.find_or_create_by()['api_key']

    def rotate_api_key(self):
        """Updates users api by replacing."""
        new_api_key = self.__generate_api_key()
        response = self.dynamo.update_item(
            Key={
                'user_id': self.user_id
            },
            AttributeUpdates={
                'api_key': {
                    'Value': new_api_key,
                    'Action': 'PUT'
                }
            }
        )
        return response

    def find_or_create_by(self):
        """
        Search for a user in dynamo.
        If no user is found create them.
        """
        search = self.__find_by_uid()
        print(search)
        if 'Item' in search:
            return search['Item']
        else:
            self.__create_user()
            search = self.__find_by_uid()
            return search['Item']

    def find(self):
        """
        Search for a user in dynamo.
        """
        search = self.__find_by_uid()
        print(search)
        if 'Item' in search:
            return search['Item']
        else:
            return None

    def destroy(self):
        """Remove a user. Don't use this outside tests.  Not atomic!"""
        response = self.__delete_user()
        if response is not None:
            return True
        else:
            return False

    def __find_by_uid(self):
        response = self.dynamo.get_item(
            Key={
                'user_id': self.user_id
            },
            AttributesToGet=[
                'user_id',
                'email',
                'api_key',
                'disabled'
            ]
        )
        return response

    def __create_user(self):
        response = self.dynamo.put_item(
            Item={
                'user_id': self.user_id,
                'email': self.email,
                'api_key': self.__generate_api_key(),
                'disabled': False

            }
        )
        return response

    def __delete_user(self):
        response = self.dynamo.delete_item(
            Key={
                'user_id': self.user_id
            }
        )
        return response

    def __generate_api_key(self):
        random_num = random.randint(0, 99999999)
        hashids = Hashids(min_length=16)
        hashid = hashids.encode(random_num)
        return hashid
