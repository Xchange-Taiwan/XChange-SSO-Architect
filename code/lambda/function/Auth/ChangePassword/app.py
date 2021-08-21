import json
import boto3

from aws import helper
from aws.helper import DeveloperMode


@DeveloperMode(True)
def lambda_handler(event, context):

    if not "authorization" in event["headers"]:
        return helper.buildResponse({"message": "Not authorized."}, 403)

    # check input
    inputJson = json.loads(event["body"])

    if not "old_password" in inputJson:
        return helper.buildResponse({"message": "Old Password is required."}, 403)

    if not "password" in inputJson:
        return helper.buildResponse({"message": "New Password is required."}, 403)

    if not "password" in inputJson:
        return helper.buildResponse({"message": "New Password is required."}, 403)

    previous_password = inputJson["old_password"]
    proposed_password = inputJson["password"]
    access_token: str = event["headers"]["authorization"]
    access_token = access_token.replace("Bearer ", "")

    if len(proposed_password) < 6:
        return helper.buildResponse(
            {"message":
                "Password must be at least 6 characters in length."}, 403
        )

    client = boto3.client("cognito-idp")

    resp, msg = client.change_password(
        PreviousPassword=previous_password,
        ProposedPassword=proposed_password,
        AccessToken=access_token,
    )

    if msg != None:
        print(msg)
        return helper.buildResponse({"message": "Error setting password."}, 403)

    return helper.buildResponse({"message": "Password has been updated."}, 200)
