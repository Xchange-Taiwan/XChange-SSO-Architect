import json
import os
import logging

from aws import helper
from aws import federate
from aws.helper import DeveloperMode

logger = logging.getLogger()
logger.setLevel(logging.INFO)

USER_POOL_ID = os.environ["USER_POOL_ID"]
USER_TABLE_NAME = os.environ["USER_TABLE_NAME"]


@DeveloperMode(True)
def lambda_handler(event, context):
    """
    Lambda function to register a new user.

    description:
        This function is used to register a new user.
        The user is registered in the user pool and the user is added to the user table.
        if platform and platform token are provided, the user is federated to the platform.

    payload:
        email: email of the user
        password: password of the user
        client_id: client id of the client
        redirect_uri: client id of the redirect_uri
        optional:
            platform: platform to federate the user to dynamodb
            platform_id_token: token to federate the user to dynamodb
            platform_access_token: access token to federate the user to dynamodb
        
    """

    input_json = dict()
    input_json = json.loads(event["body"])

    # Input data validation -----
    if not "email" in input_json:
        return helper.build_response(
            {"message": "E-mail address is required."}, 403)
    if not "password" in input_json:
        return helper.build_response({"message": "Password is required."}, 403)
    elif len(input_json["password"]) < 6:
        return helper.build_response(
            {"message": "Password must be at least 6 characters long."}, 403)
    if not "client_id" in input_json:
        return helper.build_response({"message": "`client_id` is required"},
                                     403)

    # data validated, assign to variables
    email = input_json["email"].lower()  # store all emails as lower case
    password = input_json["password"]

    # verify the client_id and redirect_uri
    if not "client_id" in input_json or not "redirect_uri" in input_json:
        return helper.build_response(
            {"message": "You do not have permission to access this resource."},
            403)

    client_id = input_json["client_id"]
    redirect_uri = input_json["redirect_uri"]

    _, msg = helper.verify_client_id_and_redirect_uri(
        user_pool_id=USER_POOL_ID,
        client_id=client_id,
        redirect_uri=redirect_uri)
    if msg != None:
        logging.info(msg)
        return helper.build_response({"message": msg}, 403)

    # build client metadata for confirmation email -----
    client_metadata = dict()
    if "agent" in input_json:
        client_metadata["agent"] = input_json["agent"]
    if "client_id" in input_json:
        client_metadata["client_id"] = input_json["client_id"]
    if "redirect_uri" in input_json:
        client_metadata["redirect_uri"] = input_json["redirect_uri"]

    # perform cognito register
    resp, msg = helper.register(user_pool_id=USER_POOL_ID,
                                username=email,
                                email=email,
                                password=password,
                                client_id=client_id,
                                client_metadata=client_metadata)
    if msg != None:
        logging.info(msg)
        return helper.build_response({"message": msg}, 403)

    # get user info
    user_cognito_id = resp["UserSub"]

    # register the federate record in the user table
    if "platform_id_token" in input_json or "platform_access_token" in input_json:

        platform_login_data = dict()
        platform_login_data["platform"] = input_json["platform"]
        if "platform_code" in input_json:
            platform_login_data["code"] = input_json["platform_code"]
        if "platform_id_token" in input_json:
            platform_login_data["id_token"] = input_json["platform_id_token"]
        if "platform_access_token" in input_json:
            platform_login_data["access_token"] = input_json[
                "platform_access_token"]

        feder_resp, msg = federate.verify_federate_and_register_or_get_user(
            user_table_name=USER_TABLE_NAME,
            platform_login_data=platform_login_data,
            user_cognito_id=user_cognito_id,
            cognito_email=email,
            mode="register")

        if msg != None:
            logging.info(msg)
            return helper.build_response({"message": msg}, 403)

    return helper.build_response({"message": msg}, 200)
