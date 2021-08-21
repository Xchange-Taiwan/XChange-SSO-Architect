import json
import boto3

from aws import helper
from aws.helper import DeveloperMode


@DeveloperMode(True)
def lambda_handler(event, context):
    inputJson = json.loads(event["body"])
    if not "code" in inputJson:
        return helper.buildResponse({"message": "Code is required."}, 403)
    if not "email" in inputJson:
        return helper.buildResponse({"message": "E-mail is required."}, 403)
    if not "client_id" in inputJson:
        return helper.buildResponse({"message": "Client ID is required."}, 403)

    # return helper.buildResponse(event)

    inputJson = json.loads(event["body"])

    code = None
    email = None

    code = inputJson["code"]
    email = inputJson["email"]
    clientID = inputJson["client_id"]

    client = boto3.client("cognito-idp")

    try:
        response = client.confirm_sign_up(
            ClientId=clientID,
            Username=email,
            ConfirmationCode=code,
            ForceAliasCreation=False,
        )

    except client.exceptions.UserNotFoundException:
        return helper.buildResponse({"message": "User not found."}, 404)
    except client.exceptions.CodeMismatchException:
        return helper.buildResponse({"message": "Code mismatch."}, 403)
    except client.exceptions.NotAuthorizedException:
        return helper.buildResponse({"message": "Not authorized."}, 403)
    except Exception as e:
        print(e.__str__())
        return helper.buildResponse({"message": e.__str__()}, 403)

    return helper.buildResponse(response, 200)
