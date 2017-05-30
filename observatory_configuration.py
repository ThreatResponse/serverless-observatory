"""Class that governs the collection of various configurations for scan data
allow the user to specify what type of environment and settings for more
fine grained insights."""

import aws
import random
import uuid

from boto3.dynamodb.conditions import Key
from hashids import Hashids


class ScanConfig(object):
    def __init__(self, user):
        self.dynamo = aws.connect_dynamo(
            table_name='observatory_configurations'
        )

        self.user = user

    def create_configuration(self, configuration_information=None):
        """Return a dictionary of the configuration for the scan."""
        config_id = uuid.uuid4().hex
        api_key = self.__generate_api_key()

        if configuration_information['notes'] == '':
            configuration_information['notes'] = "No additional infomation."
        response = self.dynamo.put_item(
            Item={
                'uuid': config_id,
                'user_id': self.user.user_id,
                'api_key': api_key,
                'config': configuration_information,
                'disabled': False

            }
        )
        return response

    def __destroy(self, config_id, user_id):
        response = self.dynamo.delete_item(
            Key={
                'uuid': config_id,
                'user_id': user_id
            }
        )
        return response

    def update_configuration(self, config):
        """Overwrite a configuration in place."""
        print(config['uuid'])
        self.__destroy(config['uuid'], config['user_id'])
        response = self.dynamo.put_item(
            Item={
                'uuid': config['uuid'],
                'user_id': config['user_id'],
                'api_key': config['api_key'],
                'config': config['config'],
                'disabled': False

            }
        )
        return response

    def rotate_api_key(self, config_id):
        """Rotate the api key for a given configuration."""
        response = self.dynamo.update_item(
            Key={
                'uuid': config_id
            },
            AttributeUpdates={
                'api_key': self.__generate_api_key()
            }
        )
        return response

    def find_config_by_id(self, config_id):
        """Locate a configuration by the uuid."""
        fe = Key('uuid').eq(config_id)

        response = self.dynamo.scan(
            FilterExpression=fe,
            Select='ALL_ATTRIBUTES'
        )

        configs = []
        for i in response['Items']:
            configs.append(i)

        return configs[0]

    def find_configs_for_user(self):
        """Return all scored configurations for a user."""
        fe = Key('user_id').eq(self.user.user_id)

        response = self.dynamo.scan(
            FilterExpression=fe,
            Select='ALL_ATTRIBUTES'
        )

        configs = []
        for i in response['Items']:
            configs.append(i)
        return configs

    def api_key(self, config_id):
        """Return the api key for the uuid of the configuration."""
        config = self.find_config_by_id(config_id)
        return config[0]['api_key']

    def __generate_api_key(self):
        """Return a unique api key."""
        random_num = random.randint(0, 99999999)
        hashids = Hashids(min_length=16)
        hashid = hashids.encode(random_num)
        return hashid
