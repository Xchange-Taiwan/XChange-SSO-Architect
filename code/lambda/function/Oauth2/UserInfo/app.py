import boto3
import logging
from aws import helper
from aws.helper import DeveloperMode

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@DeveloperMode(True)
def lambda_handler(event, context):
    """
    UserInfo Lambda Function

    description:
        This function is used to get the user information from the cognito user pool.
        The user information is used to create the user in the database.
    """
    if not "authorization" in event["headers"]:
        return helper.build_response(
            {"message": "Authorization header is missing"}, 401
        )

    authorization: str = event["headers"]["authorization"]
    access_token: str = authorization.split(" ")[1]

    cognito_client = boto3.client("cognito-idp")
    try:
        resp = cognito_client.get_user(AccessToken=access_token)
    except cognito_client.exceptions.NotAuthorizedException:
        return helper.build_response({"message": "Invalid access token"}, 401)
    except cognito_client.exceptions.UserNotFoundException:
        return helper.build_response({"message": "User not found"}, 404)
    except cognito_client.exceptions.PasswordResetRequiredException:
        return helper.build_response({"message": "Password reset required"}, 403)
    except cognito_client.exceptions.UserNotConfirmedException:
        return helper.build_response({"message": "User not confirmed"}, 403)
    except cognito_client.exceptions.UserNotFoundException:
        return helper.build_response({"message": "User not found"}, 404)
    except Exception as e:
        return helper.build_response({"message": str(e)}, 500)

    user_info = resp["UserAttributes"]
    user_info_dict = dict()
    for attribute in user_info:
        user_info_dict[attribute["Name"]] = attribute["Value"]

    return helper.build_response(user_info_dict, 200)
