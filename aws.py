"""All the things the relate to dynamodb interaction."""
import boto3
from boto3.dynamodb.conditions import Attr


def connect_dynamo(table_name):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table(table_name)
    return table


def locate_user_by_key(api_key, table_resource):
    table_resource = table_resource
    response = table_resource.scan(
        FilterExpression=Attr('api_key').eq(api_key)
    )
    items = response['Items']
    return items[0]
