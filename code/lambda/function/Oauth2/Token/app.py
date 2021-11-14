import base64
import json
import os
import logging
from urllib.parse import unquote

from aws import helper
from aws.helper import DeveloperMode

logger = logging.getLogger()
logger.setLevel(logging.INFO)

USER_POOL_ID = os.environ["USER_POOL_ID"]
USER_TABLE_NAME = os.environ["USER_TABLE_NAME"]

AUTH_CODE_TABLE_NAME = os.environ["AUTH_CODE_TABLE_NAME"]


@DeveloperMode(True)
def lambda_handler(event, context):
    """
    Token Request Handler
    """

    if not "body" in event:
        return helper.build_response({"message": "invalid_request"}, 400)

    client_id = None
    client_secret = None

    event_body_b64decoded = base64.b64decode(event["body"]).decode("utf-8")
    body_b64decoded_urldecoded = unquote(event_body_b64decoded)
    parameters = body_b64decoded_urldecoded.split("&")

    input_json = dict()
    for parameter in parameters:
        key, value = parameter.split("=")
        input_json[key] = value

    if "grant_type" not in input_json:
        return helper.build_response({"message": "invalid_request"}, 400)
    if "code" not in input_json:
        return helper.build_response({"message": "invalid_request"}, 400)

    if "redirect_uri" not in input_json:
        return helper.build_response({"message": "invalid_request"}, 400)

    if "authorization" in event["headers"]:
        authorization = event["headers"]["authorization"]
        client_id, client_secret, msg = helper.get_client_id_and_secret(authorization)
        if msg is not None:
            return helper.build_response({"message": msg}, 400)
    else:
        if "client_id" not in input_json:
            return helper.build_response({"message": "invalid_request"}, 400)
        client_id = input_json["client_id"]

    grant_type = input_json["grant_type"]
    code = input_json["code"]
    redirect_uri = input_json["redirect_uri"]

    # verify the client_id and redirect_uri
    if not "client_id" in input_json or not "redirect_uri" in input_json:
        return helper.build_response(
            {"message": "You do not have permission to access this resource."}, 403
        )

    _, msg = helper.verify_client_id_and_redirect_uri(
        user_pool_id=USER_POOL_ID, client_id=client_id, redirect_uri=redirect_uri
    )
    if msg != None:
        logging.info(msg)
        return helper.build_response({"message": msg}, 403)

    # verify the client secret
    if grant_type == "authorization_code":
        _, msg = helper.verify_client_secret(
            user_pool_id=USER_POOL_ID, client_id=client_id, client_secret=client_secret
        )
        if msg != None:
            logging.info(msg)
            return helper.build_response({"message": msg}, 403)

        # get the code
        token_set, msg = helper.get_token_from_code(
            auth_code_table_name=AUTH_CODE_TABLE_NAME, auth_code=code
        )
        if msg != None:
            logging.info(msg)
            return helper.build_response({"message": msg}, 403)
        return helper.build_response(token_set, 200)
    return helper.build_response({"message": "invalid_request"}, 400)
