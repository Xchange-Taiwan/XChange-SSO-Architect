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
            {"message": "You do not have permission to access this resource."},
            403)

    username = None
    email = None

    input_json = json.loads(event["body"])

    if not "email" in input_json:
        return helper.build_response({"message": "E-mail is required."}, 403)

    email = input_json["email"].lower()

    if not "client_id" in input_json:
        return helper.build_response({"message": "Client ID is required."},
                                     403)

    username = email

    client_id = input_json["client_id"]

    clientMetadata = dict()

    if "agent" in input_json:
        clientMetadata["agent"] = input_json["agent"]
    if "client_id" in input_json:
        clientMetadata["client_id"] = input_json["client_id"]
    if "redirect_uri" in input_json:
        clientMetadata["redirect_uri"] = input_json["redirect_uri"]

    resp, msg = helper.forgot_password(username,
                                       client_id,
                                       client_metadata=clientMetadata)

    if msg != None:
        logging.info(msg)
        return helper.build_response({"message": msg}, 403)

    return helper.build_response(
        {
            "message":
            "Please check your e-mail for password reset instructions."
        }, 200)
