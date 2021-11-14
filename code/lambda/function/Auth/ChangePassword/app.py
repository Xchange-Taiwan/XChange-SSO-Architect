import json
import boto3

from aws import helper
from aws.helper import DeveloperMode


@DeveloperMode(True)
def lambda_handler(event, context):

    if not "authorization" in event["headers"]:
        return helper.build_response({"message": "Not authorized."}, 403)

    # check input
    input_json = json.loads(event["body"])

    if not "old_password" in input_json:
        return helper.build_response({"message": "Old Password is required."}, 403)

    if not "password" in input_json:
        return helper.build_response({"message": "New Password is required."}, 403)

    if not "password" in input_json:
        return helper.build_response({"message": "New Password is required."}, 403)

    previous_password = input_json["old_password"]
    proposed_password = input_json["password"]
    access_token: str = event["headers"]["authorization"]
    access_token = access_token.replace("Bearer ", "")

    if len(proposed_password) < 6:
        return helper.build_response(
            {"message": "Password must be at least 6 characters in length."}, 403
        )

    client = boto3.client("cognito-idp")

    resp, msg = client.change_password(
        PreviousPassword=previous_password,
        ProposedPassword=proposed_password,
        AccessToken=access_token,
    )

    if msg != None:
        print(msg)
        return helper.build_response({"message": "Error setting password."}, 403)

    return helper.build_response({"message": "Password has been updated."}, 200)
