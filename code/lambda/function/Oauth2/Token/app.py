import json
import os
import logging

import requests

import boto3
from boto3.dynamodb.conditions import Key

from aws import helper
from aws import service
from aws import dynamodb_utils
from aws.helper import DeveloperMode


logger = logging.getLogger()
logger.setLevel(logging.INFO)

USER_POOL_ID = os.environ["USER_POOL_ID"]
USER_TABLE_NAME = os.environ["USER_TABLE_NAME"]
LINKEDIN_SECRET_ARN = os.environ["LINKEDIN_SECRET_ARN"]


@DeveloperMode(True)
def lambda_handler(event, context):
    # return helper.buildResponse(event)

    inputJson = json.loads(event["body"])

    password = ""  # Our auth function still requires a password but it's not used in CUSTOM_AUTH
    platform = inputJson["platform"]
    code = None
    accessToken = None
    accessTokenExpiry = None
    refreshToken = None
    refreshTokenExpiry = None
    clientID = None

    if "code" in inputJson:
        code = inputJson["code"]
    if "access_token" in inputJson:
        accessToken = inputJson["access_token"]
    # refreshToken = inputJson['refresh_token']
    clientID = inputJson["client_id"]

    userInfo = None
    response = None

    platformUserID = None
    platformUserImage = None
    platformUserFirstName = None
    platformUserLastName = None

    account = None

    tokenResponse = dict()

    secret = service.getSecret(secretName=LINKEDIN_SECRET_ARN)

    if platform == "LinkedIn":

        if code is not None:
            tokenURL = "https://www.linkedin.com/oauth/v2/accessToken"
            payload = dict()
            payload["grant_type"] = inputJson["grant_type"]
            payload["code"] = inputJson["code"]
            payload["client_id"] = secret["LINKEDIN_CLIENT_ID"]
            payload["client_secret"] = secret["LINKEDIN_CLIENT_SECRET"]
            payload["redirect_uri"] = inputJson["redirect_uri"]
            # payload['redirect_uri'] = 'http://sso.xchange.com.tw/oauth2/callback'

            response = requests.post(tokenURL, data=payload).json()

            logger.info(response)

            if "error" in response:
                return helper.buildResponse(
                    {"message": response["error_description"]}, 403
                )
            accessToken = response["access_token"]
            if "expires_in" in response:
                accessTokenExpiry = response["expires_in"]
            if "refresh_token" in response:
                refreshToken = response["refresh_token"]
            if "refresh_token_expires_in" in response:
                refreshTokenExpiry = response["refresh_token_expires_in"]

            logger.info(accessToken)

            tokenResponse["platform_access_token"] = response["access_token"]
            tokenResponse["platform_access_token_expires_in"] = response["expires_in"]
            # return helper.buildResponse(resp,200)

        if accessToken is not None:
            userInfoURL = "https://api.linkedin.com/v2/me"
            headers = {"Authorization": "Bearer " + accessToken}
            payload = dict()

            response = requests.get(userInfoURL, headers=headers).json()
            logger.info(response)

            platformUserID = response["id"]
            if "en_US" in response["firstName"]["localized"]:
                platformUserFirstName = response["firstName"]["localized"]["en_US"]
            if "en_US" in response["lastName"]["localized"]:
                platformUserLastName = response["lastName"]["localized"]["en_US"]

            profileInfoURL = (
                userInfoURL
                + "?projection=(id,profilePicture(displayImage~:playableStreams))"
            )

            response = requests.get(profileInfoURL, headers=headers).json()

            logger.info(response)

            if len(response["profilePicture"]["displayImage~"]["elements"]) > 0:
                platformUserImage = response["profilePicture"]["displayImage~"][
                    "elements"
                ][len(response["profilePicture"]["displayImage~"]["elements"]) - 1][
                    "identifiers"
                ][
                    0
                ][
                    "identifier"
                ]

        tokenResponse["platform_user_id"] = platformUserID
        tokenResponse["platform_user_first_name"] = platformUserFirstName
        tokenResponse["platform_user_last_name"] = platformUserLastName
        tokenResponse["platform_user_image"] = platformUserImage

        if platformUserID is not None:
            account = None
            logger.info("LinkedIn ID found: " + platformUserID)
            dynamodb_client = boto3.client("dynamodb")

            existingAccounts = dynamodb_client.query(
                TableName=USER_TABLE_NAME,
                IndexName="linkedin_id-index",
                KeyConditionExpression="linkedin_id = :id",
                ExpressionAttributeValues={
                    ":id": {
                        "S": str(platformUserID),
                    },
                },
            )
            # only allow linking id to new registered account not previously linked

            if len(existingAccounts["Items"]):
                account = dynamodb_utils.loads(existingAccounts["Items"][0])

    elif platform == "Facebook":
        if code is not None:
            tokenURL = "https://graph.facebook.com/v11.0/oauth/access_token"
            # accessToken =
        if accessToken is not None:
            userInfoURL = "https://graph.facebook.com/debug_token"
            # userInfo =
        pass
    elif platform == "Google":
        if code is not None:
            tokenURL = ""
            # accessToken =
        if accessToken is not None:
            userInfoURL = ""
            # userInfo =
        pass
    elif platform == "LINE":
        if code is not None:
            tokenURL = ""
            # accessToken =
        if accessToken is not None:
            userInfoURL = ""
            # userInfo =
        pass

    if not account is None:
        # if 3rd party access_token validated correctly, check we generate our own token using CUSTOM_AUTH challenge
        password = ""
        resp, msg = helper.initiateAuth(
            USER_POOL_ID,
            account["email"],
            password,
            clientID,
            authFlow="CUSTOM_AUTH",
        )

        # cognito error message check
        if msg != None:
            logger.info(msg)
            return helper.buildResponse({"message": msg}, 403)

        logger.info("CHALLENGE PASSED")
        if resp.get("AuthenticationResult"):
            logger.info("HAS RESULT")
            res = resp["AuthenticationResult"]

            tokenResponse["id_token"] = res["IdToken"]
            tokenResponse["refresh_token"] = res["RefreshToken"]
            tokenResponse["access_token"] = res["AccessToken"]
            tokenResponse["expires_in"] = res["ExpiresIn"]
            tokenResponse["token_type"] = res["TokenType"]

    logger.info(tokenResponse)
    return helper.buildResponse(tokenResponse, 200)
