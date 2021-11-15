import json
import requests
import os
import base64
import boto3

from aws import helper
from aws import dynamodb_utils
from aws.helper import DeveloperMode

from google.oauth2 import id_token as gid_token
from google.auth.transport import requests as grequests


def google_code_to_access_token(
    google_client_id, google_client_secret, google_redirect_uri, code
):
    try:
        resp = requests.post(
            "https://www.googleapis.com/oauth2/v4/token",
            data={
                "code": code,
                "client_id": google_client_id,
                "client_secret": google_client_secret,
                "redirect_uri": google_redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        if resp.status_code == 200:
            return resp.json(), None
        else:
            return None, "Invalid code."
    except Exception as e:
        return None, "Invalid code."


def verify_google_id_token(google_client_id, token):
    """
    Verify the Google ID token.
    """
    try:
        google_id_info = gid_token.verify_oauth2_token(
            token, grequests.Request(), google_client_id
        )
        if google_id_info["iss"] not in [
            "accounts.google.com",
            "https://accounts.google.com",
        ]:
            raise ValueError("Wrong issuer.")
        return google_id_info, None
    except ValueError:
        return None, "Invalid ID token."


def mapping_google_id_info_to_sso_user_info(cognito_id, cognito_email, google_id_info):
    """
    Map the Google ID token info to the user info.
    """
    sso_user_info = dict()
    sso_user_info["cognito_id"] = cognito_id
    sso_user_info["cognito_email"] = cognito_email
    sso_user_info["federated_id"] = "google" + "_" + google_id_info["sub"]
    sso_user_info["first_name"] = google_id_info["given_name"]
    sso_user_info["last_name"] = google_id_info["family_name"]
    sso_user_info["email"] = google_id_info["email"]
    sso_user_info["picture"] = google_id_info["picture"]
    return sso_user_info


def facebook_code_to_access_token(
    facebook_client_id, facebook_client_secret, facebook_redirect_uri, code
):
    try:
        resp = requests.post(
            "https://graph.facebook.com/v3.3/oauth/access_token",
            data={
                "client_id": facebook_client_id,
                "redirect_uri": facebook_redirect_uri,
                "client_secret": facebook_client_secret,
                "code": code,
            },
        )
        if resp.status_code == 200:
            return resp.json(), None
        else:
            return None, "Invalid code."
    except Exception as e:
        return None, "Invalid code."


def verify_facebook_access_token(access_token):
    """
    Verify the Facebook access token.
    """
    try:
        resp = requests.get(
            "https://graph.facebook.com/me?fields=id,name,first_name,last_name,email,picture&access_token="
            + access_token
        )
        if resp.status_code == 200:
            return resp.json(), None
        else:
            return None, "Invalid access token."
    except Exception as e:
        return None, "Invalid access token."


def mapping_facebook_user_info_to_sso_user_info(
    cognito_id, cognito_email, facebook_user_info
):
    """
    Map the Facebook ID token info to the user info.
    """
    sso_user_info = dict()
    sso_user_info["cognito_id"] = cognito_id
    sso_user_info["cognito_email"] = cognito_email
    sso_user_info["federated_id"] = "facebook" + "_" + facebook_user_info["id"]
    sso_user_info["first_name"] = facebook_user_info["first_name"]
    sso_user_info["last_name"] = facebook_user_info["last_name"]
    sso_user_info["email"] = facebook_user_info["email"]
    sso_user_info["picture"] = facebook_user_info["picture"]["data"]["url"]
    return sso_user_info


def linkedin_code_to_access_token(
    linkedin_client_id, linkedin_client_secret, linkedin_redirect_uri, code
):
    try:
        resp = requests.post(
            "https://www.linkedin.com/oauth/v2/accessToken",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": linkedin_redirect_uri,
                "client_id": linkedin_client_id,
                "client_secret": linkedin_client_secret,
            },
        )
        if resp.status_code == 200:
            return resp.json(), None
        else:
            print(resp.json())
            return None, "Invalid code."
    except Exception as e:
        print(e)
        return None, "Invalid code."


def verify_linkedin_access_token(access_token):
    """
    Verify the LinkedIn access token.
    """
    try:

        headers = {"Authorization": "Bearer " + access_token}
        resp = requests.get(
            "https://api.linkedin.com/v2/me?projection=(id,localizedFirstName,localizedLastName,vanityName,firstName,lastName,emailAddress,headline,profilePicture(displayImage~:playableStreams))",
            headers=headers,
        )
        if resp.status_code == 200:
            return resp.json(), None
        else:
            return None, "Invalid access token."
    except Exception as e:
        return None, "Invalid access token."


def mapping_linkedin_user_info_to_sso_user_info(
    cognito_id, cognito_email, linkedin_user_info
):
    """
    Map the LinkedIn ID token info to the user info.
    """
    sso_user_info = dict()
    sso_user_info["cognito_id"] = cognito_id
    sso_user_info["cognito_email"] = cognito_email
    sso_user_info["federated_id"] = "linkedin" + "_" + linkedin_user_info["id"]
    sso_user_info["first_name"] = linkedin_user_info["localizedFirstName"]
    sso_user_info["last_name"] = linkedin_user_info["localizedLastName"]
    try:
        sso_user_info["picture"] = linkedin_user_info["profilePicture"][
            "displayImage~"
        ]["elements"][0]["identifiers"][0]["identifier"]
    except Exception as e:
        sso_user_info["picture"] = ""
    return sso_user_info


def verify_federate_and_register_or_get_user(
    user_table_name,
    platform_login_data,
    mode="register",
    user_cognito_id=None,
    cognito_email=None,
):
    platform = None
    platform_id_token = None
    platform_access_token = None

    if "id_token" in platform_login_data:
        platform_id_token = platform_login_data["id_token"]
    if "access_token" in platform_login_data:
        platform_access_token = platform_login_data["access_token"]
    if "platform" in platform_login_data:
        platform = platform_login_data["platform"].lower()

        if platform == "google":
            if platform_id_token is not None:
                # Specify the CLIENT_ID of the app that accesses the backend:
                google_id_info, msg = verify_google_id_token(token=platform_id_token)
                if msg != None:
                    return None, msg

                # ID token is valid. Get the user's Google Account ID from the decoded token.
                sso_user_info = mapping_google_id_info_to_sso_user_info(
                    cognito_id=user_cognito_id,
                    cognito_email=cognito_email,
                    google_id_info=google_id_info,
                )
                if sso_user_info["federated_id"] is not None:

                    # Check if the user already exists.
                    exist_accounts, msg = query_federated_id(
                        user_table_name=user_table_name, sso_user_info=sso_user_info
                    )
                    if msg != None:
                        return None, msg

                    if mode == "register":
                        # If the record does not exist, create a new record.
                        if len(exist_accounts) == 0:
                            resp, msg = put_user_info(
                                user_table_name=user_table_name,
                                sso_user_info=sso_user_info,
                            )
                            if msg != None:
                                return None, msg
                            elif resp != None:
                                return resp, None
                        else:
                            return None, "Record already exists."
                    elif mode == "get":
                        if len(exist_accounts) == 0:
                            return None, None
                        else:
                            return exist_accounts[0], None

            return None, "Invalid platform ID token."

        elif platform == "facebook":
            if platform_access_token is not None:
                facebook_user_info, msg = verify_facebook_access_token(
                    access_token=platform_access_token
                )
                if msg != None:
                    return None, msg

                sso_user_info = mapping_facebook_user_info_to_sso_user_info(
                    cognito_id=user_cognito_id,
                    cognito_email=cognito_email,
                    facebook_user_info=facebook_user_info,
                )
                if sso_user_info["federated_id"] is not None:

                    # Check if the user already exists.
                    exist_accounts, msg = query_federated_id(
                        user_table_name=user_table_name, sso_user_info=sso_user_info
                    )
                    if msg != None:
                        return None, msg

                    if mode == "register":
                        # If the record does not exist, create a new record.
                        if len(exist_accounts) == 0:
                            resp, msg = put_user_info(
                                user_table_name=user_table_name,
                                sso_user_info=sso_user_info,
                            )
                            if msg != None:
                                return None, msg
                            elif resp != None:
                                return resp, None
                        else:
                            return None, "Record already exists."
                    elif mode == "get":
                        if len(exist_accounts) == 0:
                            return None, None
                        else:
                            return exist_accounts[0], None
        elif platform == "linkedin":
            if platform_access_token is not None:
                linkedin_user_info, msg = verify_linkedin_access_token(
                    access_token=platform_access_token
                )
                if msg != None:
                    return None, msg

                sso_user_info = mapping_linkedin_user_info_to_sso_user_info(
                    cognito_id=user_cognito_id,
                    cognito_email=cognito_email,
                    linkedin_user_info=linkedin_user_info,
                )
                if sso_user_info["federated_id"] is not None:

                    exist_accounts, msg = query_federated_id(
                        user_table_name=user_table_name, sso_user_info=sso_user_info
                    )
                    if msg != None:
                        return None, msg

                    if mode == "register":
                        # If the record does not exist, create a new record.
                        if len(exist_accounts) == 0:
                            resp, msg = put_user_info(
                                user_table_name=user_table_name,
                                sso_user_info=sso_user_info,
                            )
                            if msg != None:
                                return None, msg
                            elif resp != None:
                                return resp, None
                        else:
                            return None, "Record already exists."
                    elif mode == "get":
                        if len(exist_accounts) == 0:
                            return None, None
                        else:
                            return exist_accounts[0], None

            return None, "Invalid access token."
    return None, "Invalid platform."


def query_federated_id(user_table_name, sso_user_info):
    dynamodb_client = boto3.client("dynamodb")
    try:
        resp = dynamodb_client.query(
            TableName=user_table_name,
            IndexName="federated_id-index",
            KeyConditionExpression="federated_id = :id",
            ExpressionAttributeValues={
                ":id": {
                    "S": str(sso_user_info["federated_id"]),
                },
            },
        )
        exist_accounts = dynamodb_utils.loads(resp["Items"])
        return exist_accounts, None
    except Exception as e:
        return None, "Failed to query federated id."


def put_user_info(user_table_name, sso_user_info):
    dynamodb_client = boto3.client("dynamodb")
    try:
        resp = dynamodb_client.put_item(
            TableName=user_table_name,
            Item=dynamodb_utils.dumps(sso_user_info, as_dict=True),
            ConditionExpression="attribute_not_exists(federated_id)",
        )
        return sso_user_info, None
    except Exception as e:
        return None, e.__str__()
