import json
import requests
import os
import logging

from aws import helper
from aws import dynamodb_utils
from aws.helper import DeveloperMode

import boto3


logger = logging.getLogger()
logger.setLevel(logging.INFO)

USER_POOL_ID = os.environ["USER_POOL_ID"]
USER_TABLE_NAME = os.environ["USER_TABLE_NAME"]


@DeveloperMode(True)
def lambda_handler(event, context):
    # return helper.buildResponse(event)

    inputJson = json.loads(event["body"])

    # Input data validation -----
    if not "email" in inputJson:
        return helper.buildResponse({"message": "E-mail address is required."}, 403)
    if not "password" in inputJson:
        return helper.buildResponse({"message": "Password is required."}, 403)
    elif len(inputJson["password"]) < 6:
        return helper.buildResponse(
            {"message": "Password must be at least 6 characters long."}, 403
        )
    if not "client_id" in inputJson:
        return helper.buildResponse({"message": "`client_id` is required"}, 403)

    # if not "callback_url" in inputJson or len(inputJson["callback_url"]) == 0:
    #     return helper.buildResponse({"message": "`callback_url` is required."}, 403)

    inputJson = json.loads(event["body"])
    # data validated, assign to variables
    email = inputJson["email"].lower()  # store all emails as lower case
    password = inputJson["password"]

    # check if client ID is valid -----
    clientID = None
    if "client_id" in inputJson:
        clientID = inputJson["client_id"]

    # build client metadata for confirmation email -----
    clientMetadata = dict()
    if "agent" in inputJson:
        clientMetadata["agent"] = inputJson["agent"]
    if "client_id" in inputJson:
        clientMetadata["client_id"] = inputJson["client_id"]
    if "callback_url" in inputJson:
        clientMetadata["callback_url"] = inputJson["callback_url"]

    # perform cognito register
    resp, msg = helper.register(
        USER_POOL_ID,
        email,
        email,
        password,
        clientID,
        clientMetadata=clientMetadata,
    )
    logging.info(resp)
    logging.info(msg)
    if "platform" in inputJson:
        platform = inputJson["platform"]

        if platform == "LinkedIn":

            logging.info("platform linkedin")

            if "platform_access_token" in inputJson:
                logging.info("access token provided")
                accessToken = inputJson["platform_access_token"]
                userInfoURL = "https://api.linkedin.com/v2/me"
                headers = {"Authorization": "Bearer " + accessToken}

                response = requests.get(userInfoURL, headers=headers).json()
                logging.info(response)
                platformUserID = response["id"]

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
                if len(existingAccounts["Items"]) == 0:
                    user_item = dict()
                    user_item["cognito_id"] = resp["UserSub"]
                    user_item["email"] = email
                    user_item["linkedin_id"] = platformUserID

                    res = dynamodb_client.put_item(
                        TableName=USER_TABLE_NAME,
                        Item=dynamodb_utils.dumps(user_item, as_dict=True),
                        ConditionExpression="attribute_not_exists(cognito_id)",
                    )

    # error if message exists
    if msg != None:
        logging.info(msg)
        return helper.buildResponse({"message": msg}, 403)

    return helper.buildResponse({"message": msg}, 200)
