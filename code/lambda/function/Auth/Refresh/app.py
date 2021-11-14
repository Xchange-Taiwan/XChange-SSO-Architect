import json
import logging

from aws import helper
from aws.helper import DeveloperMode

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@DeveloperMode(True)
def lambda_handler(event, context):

    input_json = json.loads(event["body"])

    if not "refresh_token" in input_json:
        return helper.build_response({"message": "Refesh token is required."}, 403)

    if not "client_id" in input_json:
        return helper.build_response({"message": "Client ID is required."}, 403)

    refreshToken = input_json["refresh_token"]
    client_id = input_json["client_id"]
    username = None
    if "username" in input_json:
        username = input_json["username"]

    resp, msg = helper.refresh_auth(
        username=username, refreshToken=refreshToken, client_id=client_id
    )

    # error with cognito if msg is not None
    if msg != None:
        logging.info(msg)
        return helper.build_response({"message": msg}, 403)

    if resp.get("AuthenticationResult"):
        res = resp["AuthenticationResult"]
        return helper.build_response(
            {
                "id_token": res["IdToken"],
                "access_token": res["AccessToken"],
                "expires_in": res["ExpiresIn"],
                "token_type": res["TokenType"],
            },
            200,
        )
    else:  # this code block is relevant only when MFA is enabled
        return helper.build_response(
            {"error": True, "success": False, "data": None, "message": None}, 200
        )
