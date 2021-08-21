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
    # return helper.buildResponse(event)

    code = None
    username = None
    email = None
    password = None

    # check json parsing
    inputJson = json.loads(event["body"])

    if not "code" in inputJson:
        return helper.buildResponse({"message": "Code is required."}, 403)

    if not "email" in inputJson:
        return helper.buildResponse({"message": "E-mail is required."}, 403)

    if not "password" in inputJson:
        return helper.buildResponse({"message": "Password is required."}, 403)

    if not "client_id" in inputJson:
        return helper.buildResponse({"message": "Client ID is required."}, 403)

    code = inputJson["code"]
    email = inputJson["email"].lower()
    password = inputJson["password"]
    clientID = inputJson["client_id"]

    username = email

    if len(password) < 6:
        return helper.buildResponse(
            {"message":                 "Password must be at least 6 characters in length."}, 403
        )

    # cognito confirm new password using code
    resp, msg = helper.confirmForgotPassword(
        username=username, email=email, password=password, code=code, clientID=clientID
    )

    # print cognito error message
    if msg != None:
        logging.info(msg)
        return helper.buildResponse({"message": msg}, 403)

    return helper.buildResponse({"message": "Password has been reset."}, 200)
