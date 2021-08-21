import boto3
import logging
from aws import helper
from aws.helper import DeveloperMode

from i18n.locale import _, Locale


@DeveloperMode(True)
def lambda_handler(event, context):
    # Locale.init(event)
    if not "authorization" in event["headers"]:
        return helper.buildResponse({"message": _("Not authorized.")}, 403)

    access_token: str = event["headers"]["authorization"]
    access_token = access_token.replace("Bearer ", "")

    cognito_client = boto3.client("cognito-idp")
    # retrieve account with email address
    try:
        resp = cognito_client.get_user(AccessToken=access_token)
    except cognito_client.exceptions.NotAuthorizedException:
        return helper.buildResponse({"message": _("Not Authorized user.")}, 403)
    except cognito_client.exceptions.UserNotFoundException:
        return helper.buildResponse({"message": _("Unregistered user.")}, 403)
    except cognito_client.exceptions.PasswordResetRequiredException:
        return helper.buildResponse({"message": _("Please reset your password.")}, 403)
    except cognito_client.exceptions.UserNotConfirmedException:
        return helper.buildResponse({"message": _("Please verify your email.")}, 403)
    except cognito_client.exceptions.UserNotFoundException:
        return helper.buildResponse({"message": _("Unregistered user.")}, 403)
    except Exception as e:
        return helper.buildResponse({"message": _(e)}, 403)

    response = dict()

    response["ssoUserId"] = resp["Username"]
    for attribute in resp["UserAttributes"]:
        if attribute["Name"] == "email":
            response["email"] = attribute["Value"]

    return helper.buildResponse(response, 200)