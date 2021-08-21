import os
import logging

from aws import helper
from aws.helper import DeveloperMode

import boto3


logger = logging.getLogger()
logger.setLevel(logging.INFO)

USER_POOL_ID = os.environ["USER_POOL_ID"]


@DeveloperMode(True)
def lambda_handler(event, context):
    email = None
    if "queryStringParameters" in event:
        if "email" in event["queryStringParameters"]:
            email = event["queryStringParameters"]["email"]
    if email is None:
        return helper.buildResponse(False)

    client = boto3.client("cognito-idp")
    try:
        resp = client.admin_get_user(UserPoolId=USER_POOL_ID, Username=email)
    except client.exceptions.UserNotFoundException as e:
        return helper.buildResponse(True)
    except Exception as e:
        return helper.buildResponse(False)
    return helper.buildResponse(False)
