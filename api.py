"""Class the governs all showdown-api operations."""
import aws
import user
import uuid


class Profiler(object):
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.dynamo = aws.connect_dynamo(table_name='observatory_scans')

        if api_key is not None:
            self.authenticated = self.__authenticate()
        else:
            self.authenticated = False

    def __authenticate(self):
        """Check to see if api key is valid."""

        # Search dynamo for user having api_key\
        api_key = APIKey(self.api_key)
        self.config = api_key.locate_configuration()
        print(self.config)
        if self.config['disabled'] is True:
            return False
        elif self.config['api_key'] == self.api_key:
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
        profile['user_id'] = self.config['user_id']
        profile['uuid'] = self.__uuid()
        profile['config_id'] = self.config['uuid']

        # Store the record in dynamodb
        try:
            self.dynamo.put_item(
                Item=profile
            )
            return profile['uuid']
        except Exception as e:
            raise(e)
            return None

    def destroy_profile(self, uuid):
        response = self.dynamo.delete_item(
            Key={
                'uuid': uuid
            }
        )
        return response


"""First class object to run DynamoDB scans to correlate user."""


class APIKey(object):
    def __init__(self, api_key):
        self.api_key = api_key
        self.dynamo_u = aws.connect_dynamo(table_name='observatory_users')
        self.dynamo_c = aws.connect_dynamo(
            table_name='observatory_configurations'
        )

    def __scan_for_user(self):
        """Query dynamo for a user record matching the api key."""
        item = aws.locate_user_by_key(
            api_key=self.api_key,
            table_resource=self.dynamo_u
        )
        return item

    def __scan_for_config(self):
        """Query dynamo for a user record matching the api key."""
        item = aws.locate_config_by_key(
            api_key=self.api_key,
            table_resource=self.dynamo_c
        )
        return item

    def locate_user(self):
        """Init a dynamo connection and search for the corresponding user."""
        result = self.__scan_for_user()
        this_user = user.User(userinfo=result).find()
        if this_user is not None:
            return this_user
        else:
            return None

    def locate_configuration(self):
        """Init a dynamo connection and search for the corresponding user."""
        result = self.__scan_for_config()
        return result
