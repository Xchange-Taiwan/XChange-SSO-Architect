import json
import os
import base64
import logging

from aws import helper
from aws import federate
from aws.helper import DeveloperMode

logger = logging.getLogger()
logger.setLevel(logging.INFO)

USER_POOL_ID = os.environ["USER_POOL_ID"]
USER_TABLE_NAME = os.environ["USER_TABLE_NAME"]

AUTH_CODE_TABLE_NAME = os.environ["AUTH_CODE_TABLE_NAME"]


@DeveloperMode(True)
def lambda_handler(event, context):
    """
    Lambda handler for the Auth/Login API.

    description:
        This function is used to authenticate a user.
        The user is authenticated by providing a username and password then returned a JWT token.
        if the user is not found or the password is incorrect, an error is returned.
        if platform and platform token are provided, the user is federated to the platform.

    headers:
        Authorization: Basic base64(username:password)

    payload:
        client_id: client id of the client
        redirect_uri: callback url of the client
        optional:
            platform: platform to federate the user to dynamodb
            platform_id_token: token to federate the user to dynamodb
            platform_access_token: access token to federate the user to dynamodb

    """

    if not "headers" in event:
        return helper.build_response(
            {"message": "You do not have permission to access this resource."}, 403
        )

    if not "authorization" in event["headers"]:
        return helper.build_response(
            {"message": "You do not have permission to access this resource."}, 403
        )

    if not "body" in event:
        return helper.build_response(
            {"message": "You do not have permission to access this resource."}, 403
        )

    input_json = dict()
    input_json = json.loads(event["body"])

    auth = event["headers"]["authorization"]
    parts = auth.split(" ")

    # only support Basic auth
    if parts[0] != "Basic":
        return helper.build_response(
            {"message": "Unsupported authentication method."}, 403
        )

    auth = base64.b64decode(parts[1]).decode("UTF-8")

    parts = auth.split(":", 1)
    email = parts[0].lower()
    password = parts[1]

    response_type = "code"
    if "response_type" in input_json:
        response_type = input_json["response_type"]

    # verify the client_id and redirect_uri
    if not "client_id" in input_json or not "redirect_uri" in input_json:
        return helper.build_response(
            {"message": "You do not have permission to access this resource."}, 403
        )

    client_id = input_json["client_id"]
    redirect_uri = input_json["redirect_uri"]

    _, msg = helper.verify_client_id_and_redirect_uri(
        user_pool_id=USER_POOL_ID, client_id=client_id, redirect_uri=redirect_uri
    )
    if msg != None:
        logging.info(msg)
        return helper.build_response({"message": msg}, 403)

    # login with email and password
    resp, msg = helper.initiate_auth(
        user_pool_id=USER_POOL_ID,
        client_id=client_id,
        username=email,
        password=password,
    )
    if msg != None:
        logging.info(msg)
        return helper.build_response({"message": msg}, 403)

    # get the user info
    id_token = resp["AuthenticationResult"]["IdToken"]
    user_cognito_id, msg = helper.get_cognito_username_from_id_token(id_token)
    if msg != None:
        logging.info(msg)
        return helper.build_response({"message": msg}, 403)

    # register the federate record in the user table
    if "platform_id_token" in input_json or "platform_access_token" in input_json:

        platform_login_data = dict()
        platform_login_data["platform"] = input_json["platform"]
        if "platform_code" in input_json:
            platform_login_data["code"] = input_json["platform_code"]
        if "platform_id_token" in input_json:
            platform_login_data["id_token"] = input_json["platform_id_token"]
        if "platform_access_token" in input_json:
            platform_login_data["access_token"] = input_json["platform_access_token"]

        feder_resp, msg = federate.verify_federate_and_register_or_get_user(
            user_table_name=USER_TABLE_NAME,
            platform_login_data=platform_login_data,
            user_cognito_id=user_cognito_id,
            cognito_email=email,
            mode="register",
        )

        if msg != None:
            logging.info(msg)
            return helper.build_response({"message": msg}, 403)

    # return the JWT token
    if "AuthenticationResult" in resp:
        formatted_authentication_result = helper.format_authentication_result(resp)

        if response_type == "code":
            # get the authorization code
            auth_code, msg = helper.store_token_to_dynamodb_and_get_auth_code(
                auth_code_table_name=AUTH_CODE_TABLE_NAME,
                client_id=client_id,
                redirect_uri=redirect_uri,
                token_set=formatted_authentication_result,
            )
            if msg != None:
                logging.info(msg)
                return helper.build_response({"message": msg}, 403)

            # return the authorization code
            return helper.build_response({"code": auth_code}, 200)

        elif response_type == "token":
            return helper.build_response(formatted_authentication_result, 200)

        else:
            return helper.build_response({"message": "Unsupported response type."}, 403)

    return helper.build_response({"message": "Invalid username or password."}, 403)
