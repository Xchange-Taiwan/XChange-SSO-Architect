import json
import logging

from aws import helper
from aws.helper import DeveloperMode


logger = logging.getLogger()
logger.setLevel(logging.INFO)


@DeveloperMode(True)
def lambda_handler(event, context):

    inputJson = json.loads(event["body"])

    if not "refresh_token" in inputJson:
        return helper.buildResponse({"message": "Refesh token is required."}, 403)

    if not "client_id" in inputJson:
        return helper.buildResponse({"message": "Client ID is required."}, 403)

    refreshToken = inputJson["refresh_token"]
    clientID = inputJson["client_id"]
    username = None
    if "username" in inputJson:
        username = inputJson["username"]

    resp, msg = helper.refreshAuth(
        username=username, refreshToken=refreshToken, clientID=clientID
    )

    # error with cognito if msg is not None
    if msg != None:
        logging.info(msg)
        return helper.buildResponse({"message": msg}, 403)

    if resp.get("AuthenticationResult"):
        res = resp["AuthenticationResult"]
        return helper.buildResponse(
            {
                "id_token": res["IdToken"],
                "access_token": res["AccessToken"],
                "expires_in": res["ExpiresIn"],
                "token_type": res["TokenType"],
            },
            200,
        )
    else:  # this code block is relevant only when MFA is enabled
        return helper.buildResponse(
            {"error": True, "success": False, "data": None, "message": None}, 200
        )
