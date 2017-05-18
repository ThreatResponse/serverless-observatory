"""Class the governs all showdown-api operations."""
import user
import aws


class Profiler(object):
    def __init__(self, api_key):
        self.api_key = api_key
        self.dynamo = aws.connect_dynamo(table_name='observatory_users')
        self.authenticated = self.__authenticate()

    def __authenticate(self):
        """Check to see if api key is valid."""

        # Search dynamo for user having api_key\
        api_key = APIKey(self.api_key)
        u = api_key.locate_user()

        if u['api_key'] == self.api_key and u['disabled'] is False:
            # If key present and not disabled return true
            return True
        else:
            # If key not present or disabled return false
            return False

    def store_profile(self, profile):

        # Ingest the output of the serverless profiler as json

        # Sanitize the json safely

        # Store the record in dynamodb
        pass


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
