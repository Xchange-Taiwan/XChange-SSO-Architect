import json
import boto3

from aws import helper
from aws.helper import DeveloperMode


@DeveloperMode(True)
def lambda_handler(event, context):
    input_json = json.loads(event["body"])
    if not "code" in input_json:
        return helper.build_response({"message": "Code is required."}, 403)
    if not "email" in input_json:
        return helper.build_response({"message": "E-mail is required."}, 403)
    if not "client_id" in input_json:
        return helper.build_response({"message": "Client ID is required."}, 403)

    # return helper.buildResponse(event)

    input_json = json.loads(event["body"])

    code = None
    email = None

    code = input_json["code"]
    email = input_json["email"]
    client_id = input_json["client_id"]

    cognito_client = boto3.client("cognito-idp")

    try:
        response = cognito_client.confirm_sign_up(
            ClientId=client_id,
            Username=email,
            ConfirmationCode=code,
            ForceAliasCreation=False,
        )
    except cognito_client.exceptions.UserNotFoundException:
        return helper.build_response({"message": "User not found."}, 404)
    except cognito_client.exceptions.CodeMismatchException:
        return helper.build_response({"message": "Code mismatch."}, 403)
    except cognito_client.exceptions.NotAuthorizedException:
        return helper.build_response({"message": "Not authorized."}, 403)
    except Exception as e:
        print(e.__str__())
        return helper.build_response({"message": e.__str__()}, 403)

    return helper.build_response(response, 200)
