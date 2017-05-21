"""Class the governs all showdown-api operations."""
import aws
import json
import user
import uuid

class Profiler(object):
    def __init__(self, api_key):
        self.api_key = api_key
        self.dynamo = aws.connect_dynamo(table_name='observatory_scans')
        self.authenticated = self.__authenticate()

    def __authenticate(self):
        """Check to see if api key is valid."""

        # Search dynamo for user having api_key\
        api_key = APIKey(self.api_key)
        self.user = api_key.locate_user()

        if self.user['disabled'] is True:
            return False
        elif self.user['api_key'] == self.api_key:
            # If key present and not disabled return true
            return True
        else:
            # If key not present or disabled return false
            return False

    def __uuid(self):
        return uuid.uuid4().hex

    def store_profile(self, profile):
        # Ingest the output of the serverless profiler as json

        # Add a UUID to the json object
        profile['uuid'] = self.__uuid()
        profile['user_id'] = self.user['user_id']

        # Store the record in dynamodb
        try:
            response = self.dynamo.put_item(
                Item=profile
            )
            print(response)
            return profile['uuid']
        except Exception as e:
            raise(e)
            return None

    def destroy_profile(self, profile_id):
        response = self.dynamo.delete_item(
            Key={
                'uuid': profile_id
            }
        )
        return response


"""First class object to run DynamoDB scans to correlate user."""


class APIKey(object):
    def __init__(self, api_key):
        self.api_key = api_key
        self.dynamo = aws.connect_dynamo(table_name='observatory_users')

    def __scan(self):
        """Query dynamo for a user record matching the api key."""
        item = aws.locate_user_by_key(
            api_key=self.api_key,
            table_resource=self.dynamo
        )
        return item

    def locate_user(self):
        """Init a dynamo connection and search for the corresponding user."""
        result = self.__scan()
        this_user = user.User(userinfo=result).find()
        if this_user is not None:
            return this_user
        else:
            return None
