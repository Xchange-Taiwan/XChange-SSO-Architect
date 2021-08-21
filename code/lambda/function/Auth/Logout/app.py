import os
import boto3
import logging

from aws import helper
from aws.helper import DeveloperMode


logger = logging.getLogger()
logger.setLevel(logging.INFO)

USER_POOL_ID = os.environ["USER_POOL_ID"]


def logout(userPoolID, username):
    client = boto3.client("cognito-idp")

    try:
        resp = client.admin_user_global_sign_out(
            UserPoolId=userPoolID, Username=username
        )
    except Exception as e:
        logging.info("Logout Error:" + e.__str__())
        return None, e.__str__()

    return resp, None


@DeveloperMode(True)
def lambda_handler(event, context):

    claims = event["requestContext"]["authorizer"]["claims"]
    username = claims["cognito:username"]

    resp, msg = logout(userPoolID=USER_POOL_ID, username=username)

    if msg != None:
        logging.info(msg)
        return helper.buildResponse({"message": "Error setting new password."}, 403)

    logging.info(resp)
    return helper.buildResponse({"message": "Logged out."})
