import json
import logging

from aws import helper
from aws.helper import DeveloperMode

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@DeveloperMode(True)
def lambda_handler(event, context):
    if event["body"] is None:
        return helper.build_response(
            {"message": "You do not have permission to access this resource."}, 403
        )
    # return helper.buildResponse(event)

    code = None
    username = None
    email = None
    password = None

    # check json parsing
    input_json = json.loads(event["body"])

    if not "code" in input_json:
        return helper.build_response({"message": "Code is required."}, 403)

    if not "email" in input_json:
        return helper.build_response({"message": "E-mail is required."}, 403)

    if not "password" in input_json:
        return helper.build_response({"message": "Password is required."}, 403)

    if not "client_id" in input_json:
        return helper.build_response({"message": "Client ID is required."}, 403)

    code = input_json["code"]
    email = input_json["email"].lower()
    password = input_json["password"]
    client_id = input_json["client_id"]

    username = email

    if len(password) < 6:
        return helper.build_response(
            {"message": "Password must be at least 6 characters in length."}, 403
        )

    # cognito confirm new password using code
    resp, msg = helper.confirm_forgot_password(
        username=username,
        email=email,
        password=password,
        code=code,
        client_id=client_id,
    )

    # print cognito error message
    if msg != None:
        logging.info(msg)
        return helper.build_response({"message": msg}, 403)

    return helper.build_response({"message": "Password has been reset."}, 200)
