import json
import os
import base64
import logging

import boto3

from aws import helper
from aws.helper import DeveloperMode


logger = logging.getLogger()
logger.setLevel(logging.INFO)

USER_POOL_ID = os.environ["USER_POOL_ID"]


@DeveloperMode(True)
def lambda_handler(event, context):
    if not "headers" in event:
        return helper.buildResponse(
            {"message": "You do not have permission to access this resource."}, 403
        )

    if not "authorization" in event["headers"]:
        return helper.buildResponse(
            {"message": "You do not have permission to access this resource."}, 403
        )

    if not "body" in event or "client_id" not in event["body"]:
        return helper.buildResponse(
            {"message": "You do not have permission to access this resource."}, 403
        )

    auth = event["headers"]["authorization"]
    parts = auth.split(" ")

    # only support Basic auth
    if parts[0] != "Basic":
        return helper.buildResponse(
            {"message": "Unsupported authentication method."}, 403
        )

    auth = base64.b64decode(parts[1]).decode("UTF-8")

    parts = auth.split(":", 1)
    email = parts[0].lower()
    password = parts[1]

    inputJson = dict()
    inputJson = json.loads(event["body"])
    clientID = inputJson["client_id"]

    cognito_client = boto3.client("cognito-idp")

    # retrieve account with email address
    try:
        resp, msg = helper.initiateAuth(
            USER_POOL_ID, email, password, clientID)
    except cognito_client.exceptions.NotAuthorizedException:
        return helper.buildResponse({"message": "Not Authorized user."}, 403)
    except cognito_client.exceptions.UserNotFoundException:
        return helper.buildResponse({"message": "Unregistered user."}, 403)
    except cognito_client.exceptions.PasswordResetRequiredException:
        return helper.buildResponse({"message": "Please reset your password."}, 403)
    except cognito_client.exceptions.UserNotConfirmedException:
        return helper.buildResponse({"message": "Please verify your email."}, 403)
    except cognito_client.exceptions.UserNotFoundException:
        return helper.buildResponse({"message": "Unregistered user."}, 403)
    except Exception as e:
        return helper.buildResponse({"message": e}, 403)

    # cognito error message check
    if msg != None:
        logging.info(msg)
        return helper.buildResponse({"message": msg}, 403)

    if resp.get("AuthenticationResult"):

        res = resp["AuthenticationResult"]
        response = dict()
        # response['account_id'] = account['_id']
        response["id_token"] = res["IdToken"]
        response["refresh_token"] = res["RefreshToken"]
        response["access_token"] = res["AccessToken"]
        response["expires_in"] = res["ExpiresIn"]
        response["token_type"] = res["TokenType"]
        return helper.buildResponse(response, 200)

    else:  # this code block is relevant only when MFA is enabled
        return helper.buildResponse(resp, 200)
        # return helper.buildResponse({"error": True, "success": False, "data": None, "message": None}, 200)
