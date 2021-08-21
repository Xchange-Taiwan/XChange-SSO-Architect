import json
import logging

from aws import helper
from aws.helper import DeveloperMode


logger = logging.getLogger()
logger.setLevel(logging.INFO)


@DeveloperMode(True)
def lambda_handler(event, context):
    if event["body"] is None:
        return helper.buildResponse(
            {"message": "You do not have permission to access this resource."}, 403
        )

    username = None
    email = None

    inputJson = json.loads(event["body"])

    if not "email" in inputJson:
        return helper.buildResponse({"message": "E-mail is required."}, 403)

    email = inputJson["email"].lower()

    if not "client_id" in inputJson:
        return helper.buildResponse({"message": "Client ID is required."}, 403)

    username = email

    clientID = inputJson["client_id"]

    clientMetadata = dict()

    if "agent" in inputJson:
        clientMetadata["agent"] = inputJson["agent"]
    if "client_id" in inputJson:
        clientMetadata["client_id"] = inputJson["client_id"]
    if "callback_url" in inputJson:
        clientMetadata["callback_url"] = inputJson["callback_url"]

    resp, msg = helper.forgotPassword(
        username, clientID, clientMetadata=clientMetadata)

    if msg != None:
        logging.info(msg)
        return helper.buildResponse({"message": msg}, 403)

    return helper.buildResponse(
        {"message":             "Please check your e-mail for password reset instructions."}, 200
    )
