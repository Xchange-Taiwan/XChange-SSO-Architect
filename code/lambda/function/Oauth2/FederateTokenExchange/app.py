import json
import os
import logging

import boto3

from aws import helper
from aws import federate
from aws.helper import DeveloperMode

logger = logging.getLogger()
logger.setLevel(logging.INFO)

USER_POOL_ID = os.environ["USER_POOL_ID"]
USER_TABLE_NAME = os.environ["USER_TABLE_NAME"]

AUTH_CODE_TABLE_NAME = os.environ["AUTH_CODE_TABLE_NAME"]

LINKEDIN_SECRET_ARN = (
    os.environ["LINKEDIN_SECRET_ARN"] if "LINKEDIN_SECRET_ARN" in os.environ else None
)
FACEBOOK_SECRET_ARN = (
    os.environ["FACEBOOK_SECRET_ARN"] if "FACEBOOK_SECRET_ARN" in os.environ else None
)
GOOGLE_SECRET_ARN = (
    os.environ["GOOGLE_SECRET_ARN"] if "GOOGLE_SECRET_ARN" in os.environ else None
)


@DeveloperMode(True)
def lambda_handler(event, context):
    """
    Federate Token Exchange Lambda Function
    """

    if not "body" in event:
        return helper.build_response(
            {"message": "You do not have permission to access this resource."}, 403
        )

    input_json = dict()
    input_json = json.loads(event["body"])

    # verify the client_id and redirect_uri
    if not "client_id" in input_json or not "redirect_uri" in input_json:
        return helper.build_response(
            {"message": "You do not have permission to access this resource."}, 403
        )

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

    federate_account = None
    platform = input_json["platform"].lower()

    platform_login_data = dict()
    platform_login_data["platform"] = platform

    # register the federate record in the user table
    if (
        "id_token" in input_json
        or "access_token" in input_json
        or "platform_code" in input_json
    ):

        if "code" in input_json:
            platform_code = input_json["platform_code"]

            secret_client = boto3.client("secretsmanager", region_name="ap-southeast-1")

            if platform == "linkedin":
                secret = secret_client.get_secret_value(SecretId=LINKEDIN_SECRET_ARN)
                secret_dict = json.loads(secret["SecretString"])
                platform_client_id = secret_dict["client_id"]
                platform_client_secret = secret_dict["client_secret"]
                if "platform_redirect_uri" not in input_json:
                    return helper.build_response(
                        {
                            "message": "You do not have permission to access this resource."
                        },
                        403,
                    )
                platform_redirect_uri = input_json["platform_redirect_uri"]

                resp, msg = federate.linkedin_code_to_access_token(
                    linkedin_client_id=platform_client_id,
                    linkedin_client_secret=platform_client_secret,
                    linkedin_redirect_uri=platform_redirect_uri,
                    code=platform_code,
                )
                if msg != None:
                    logging.info(msg)
                    return helper.build_response({"message": msg}, 403)
                platform_login_data["access_token"] = resp["access_token"]

            elif platform == "facebook":
                secret = secret_client.get_secret_value(SecretId=FACEBOOK_SECRET_ARN)
                secret_dict = json.loads(secret["SecretString"])
                platform_client_id = secret_dict["client_id"]
                platform_client_secret = secret_dict["client_secret"]
                resp, msg = federate.facebook_code_to_access_token(
                    facebook_client_id=platform_client_id,
                    facebook_client_secret=platform_client_secret,
                    code=platform_code,
                )
                if msg != None:
                    logging.info(msg)
                    return helper.build_response({"message": msg}, 403)
                platform_login_data["access_token"] = resp["access_token"]

            elif platform == "google":
                secret = secret_client.get_secret_value(SecretId=GOOGLE_SECRET_ARN)
                secret_dict = json.loads(secret["SecretString"])
                platform_client_id = secret_dict["client_id"]
                platform_client_secret = secret_dict["client_secret"]
                resp, msg = federate.google_code_to_access_token(
                    google_client_id=platform_client_id,
                    google_client_secret=platform_client_secret,
                    code=platform_code,
                )
                if msg != None:
                    logging.info(msg)
                    return helper.build_response({"message": msg}, 403)
                platform_login_data["access_token"] = resp["access_token"]

        if "id_token" in input_json:
            platform_login_data["id_token"] = input_json["id_token"]
        if "access_token" in input_json:
            platform_login_data["access_token"] = input_json["access_token"]

        federate_account, msg = federate.verify_federate_and_register_or_get_user(
            user_table_name=USER_TABLE_NAME,
            platform_login_data=platform_login_data,
            mode="get",
        )

        if msg != None:
            logging.info(msg)
            return helper.build_response({"message": msg}, 403)

    token_response = dict()
    token_response["platform"] = platform
    if "id_token" in platform_login_data:
        token_response["platform_id_token"] = platform_login_data["id_token"]
    if "access_token" in platform_login_data:
        token_response["platform_access_token"] = platform_login_data["access_token"]

    if not federate_account is None:
        # if 3rd party access_token validated correctly, check we generate our own token using CUSTOM_AUTH challenge
        password = ""
        resp, msg = helper.initiate_auth(
            USER_POOL_ID,
            federate_account["cognito_email"],
            password,
            client_id,
            auth_flow="CUSTOM_AUTH",
        )

        # cognito error message check
        if msg != None:
            logger.info(msg)
            return helper.build_response({"message": msg}, 403)

        logger.info("CHALLENGE PASSED")
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
                token_response["access_token"] = formatted_authentication_result[
                    "access_token"
                ]
                token_response["id_token"] = formatted_authentication_result["id_token"]
                token_response["refresh_token"] = formatted_authentication_result[
                    "refresh_token"
                ]
                token_response["expires_in"] = formatted_authentication_result[
                    "expires_in"
                ]
                token_response["token_type"] = formatted_authentication_result[
                    "token_type"
                ]

            else:
                return helper.build_response(
                    {"message": "Unsupported response type."}, 403
                )

    logger.info(token_response)
    return helper.build_response(token_response, 200)
