import boto3
import botocore.exceptions
import base64
import json
import hmac
import hashlib
import traceback
import uuid
import time

import re

from aws import dynamodb_utils


class Helper:
    EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")


def represents_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def cognito_authorizer(event):
    claims = event["requestContext"]["authorizer"]["claims"]
    return claims


def get_secret_hash(username, client_id, client_secret):
    msg = username + client_id
    dig = hmac.new(
        str(client_secret).encode("utf-8"),
        msg=str(msg).encode("utf-8"),
        digestmod=hashlib.sha256,
    ).digest()
    d2 = base64.b64encode(dig).decode()
    return d2


def delete_user(user_pool_id, username):
    client = boto3.client("cognito-idp")
    try:
        resp = client.admin_delete_user(UserPoolId=user_pool_id, Username=username)
    except Exception as e:
        return None, e.__str__()

    return resp, None


def get_user(user_pool_id, username):
    client = boto3.client("cognito-idp")
    try:
        resp = client.admin_get_user(UserPoolId=user_pool_id, Username=username)
    except Exception as e:
        return None, e.__str__()

    return resp, None


def admin_create_user(user_pool_id, email, password):
    client = boto3.client("cognito-idp")

    try:
        resp = client.admin_create_user(
            UserPoolId=user_pool_id,
            Username=email,
            UserAttributes=[
                {"Name": "email", "Value": email},
                {"Name": "email_verified", "Value": "true"},
            ],
            MessageAction="SUPPRESS",
        )
    except client.exceptions.UsernameExistsException:
        print(email)
        print("Exception - User Exists")
        return None, "User already exists."
    except Exception as e:
        print(email)
        print("Exception - Other")
        print(e.__str__())
        return None, e.__str__()

    cognitoUsername = resp["User"]["Username"]

    try:
        passwordResp = client.admin_set_user_password(
            UserPoolId=user_pool_id,
            Username=cognitoUsername,
            Password=password,
            Permanent=True,
        )
    except Exception as e:
        print("Exception - Other Password Set")
        print(e.__str__())

    return resp, None


def admin_confirm_signUp(
    user_pool_id,
    username,
    email=None,
    client_id=None,
    client_secret=None,
    client_metadata=dict(),
):
    client = boto3.client("cognito-idp")

    if not client_secret is None:
        secretHash = get_secret_hash(username, client_id, client_secret)

    try:
        if not client_secret is None:
            resp = client.admin_confirm_sign_up(
                UserPoolId=user_pool_id,
                Username=username,
            )
        else:
            resp = client.admin_confirm_sign_up(
                UserPoolId=user_pool_id,
                Username=username,
            )
    except client.exceptions.UserNotFoundException:
        return None, "User not found."
    except client.exceptions.CodeMismatchException:
        return None, "Code mismatch."
    except client.exceptions.NotAuthorizedException:
        return None, "Not authorized."
    except Exception as e:
        return None, e.__str__()

    return resp, None


def confirm_sign_up(
    username, email, code, client_id, client_secret=None, client_metadata=dict()
):
    client = boto3.client("cognito-idp")

    if not client_secret is None:
        secretHash = get_secret_hash(username, client_id, client_secret)

    try:
        resp = client.confirm_sign_up(
            ClientId=client_id,
            Username=username,
            ConfirmationCode=code,
            ForceAliasCreation=False,
        )

    except client.exceptions.UserNotFoundException:
        return None, "User not found."
    except client.exceptions.CodeMismatchException:
        return None, "Code mismatch."
    except client.exceptions.NotAuthorizedException:
        return None, "Not authorized."
    except Exception as e:
        return None, e.__str__()

    return resp, None


def confirm_forgot_password(
    username,
    email,
    password,
    code,
    client_id,
    client_secret=None,
    client_metadata=dict(),
):
    client = boto3.client("cognito-idp")

    if not client_secret is None:
        secretHash = get_secret_hash(username, client_id, client_secret)

    try:
        resp = client.confirm_forgot_password(
            ClientId=client_id,
            Username=username,
            ConfirmationCode=code,
            Password=password,
        )

    except client.exceptions.UserNotFoundException as e:
        return None, "User not found."
    except client.exceptions.CodeMismatchException as e:
        return None, "Code mismatch."
    except client.exceptions.NotAuthorizedException as e:
        return None, "Not authorized."
    except Exception as e:
        return None, e.__str__()

    return resp, None


def register(
    user_pool_id,
    username,
    email,
    password,
    client_id,
    client_secret=None,
    client_metadata=dict(),
):
    cognito_client = boto3.client("cognito-idp")
    userAttributes = list()
    userAttribute = dict()
    userAttribute["Name"] = "email"
    userAttribute["Value"] = email

    userAttributes.append(userAttribute)

    if not client_secret is None:
        secretHash = get_secret_hash(username, client_id, client_secret)

    try:
        if not client_secret is None:
            resp = cognito_client.sign_up(
                ClientId=client_id,
                SecretHash=secretHash,
                Username=email,
                Password=password,
                UserAttributes=userAttributes,
                ClientMetadata=client_metadata,
            )
        else:
            resp = cognito_client.sign_up(
                ClientId=client_id,
                Username=email,
                Password=password,
                UserAttributes=userAttributes,
                ClientMetadata=client_metadata,
            )

    except cognito_client.exceptions.UsernameExistsException as e:
        return None, "Username exists."
    except cognito_client.exceptions.InvalidPasswordException as e:
        return None, "Invalid password."
    except cognito_client.exceptions.UserLambdaValidationException as e:
        return None, "User lambda validation."
    except Exception as e:
        return None, e.__str__()

    return resp, None


def resend_confirm(username, client_id, client_secret=None, client_metadata=dict()):
    client = boto3.client("cognito-idp")

    if not client_secret is None:
        secretHash = get_secret_hash(username, client_id, client_secret)

    try:
        resp = client.resend_confirmation_code(
            ClientId=client_id, Username=username, ClientMetadata=client_metadata
        )

    except client.exceptions.UserNotFoundException:
        return None, "User not found."
    except client.exceptions.InvalidParameterException:
        return None, "Invalid parameter."
    except Exception as e:
        return None, e.__str__()

    return resp, None


def forgot_password(username, client_id, client_secret=None, client_metadata=dict()):
    client = boto3.client("cognito-idp")

    if not client_secret is None:
        secretHash = get_secret_hash(username, client_id, client_secret)

    try:
        resp = client.forgot_password(
            ClientId=client_id, Username=username, ClientMetadata=client_metadata
        )

    except client.exceptions.UserNotFoundException:
        return None, "User not found."
    except client.exceptions.InvalidParameterException:
        return None, "Invalid parameter."
    except client.exceptions.CodeMismatchException:
        return None, "Code mismatch."
    except client.exceptions.NotAuthorizedException:
        return None, "Not authorized."
    except Exception as e:
        return None, e.__str__()

    return resp, None


# def refreshAuth(user_pool_id, username, refreshToken, client_id, client_secret):
def refresh_auth(username, refreshToken, client_id, client_secret=None):

    client = boto3.client("cognito-idp")

    authParameters = dict()
    authParameters["REFRESH_TOKEN"] = refreshToken

    if not client_secret is None:
        authParameters["SECRET_HASH"] = get_secret_hash(
            username, client_id, client_secret
        )

    try:
        resp = client.initiate_auth(
            ClientId=client_id,
            AuthFlow="REFRESH_TOKEN_AUTH",
            AuthParameters=authParameters,
        )

    except client.exceptions.NotAuthorizedException as e:
        return None, "Not authorized."
    except client.exceptions.UserNotConfirmedException as e:
        return None, "User not confirmed."
    except Exception as e:
        return None, e.__str__()

    return resp, None


def initiate_auth(
    user_pool_id,
    username,
    password,
    client_id,
    client_secret=None,
    auth_flow="USER_PASSWORD_AUTH",
):
    """
    Initiate an authentication request.

    Args:
        user_pool_id (str): The user pool ID.
        username (str): The username.
        password (str): The password.
        client_id (str): The client ID.
        client_secret (str): The client secret.
        auth_flow (str): The authentication flow.

    Returns:
        dict: The response.
        str: The error message.
    """
    client = boto3.client("cognito-idp")

    auth_parameters = dict()
    client_metadata = dict()

    auth_parameters["USERNAME"] = username
    client_metadata["username"] = username
    auth_parameters["PASSWORD"] = password
    client_metadata["password"] = password

    # Client credential
    if auth_flow == "ADMIN_NO_SRP_AUTH":
        auth_parameters["PASSWORD"] = password
        client_metadata["password"] = password

    # Challenge flow
    elif auth_flow == "CUSTOM_AUTH":
        pass

    # get client_secret if it exists
    if client_secret is None:
        client_secret, msg = get_client_secret(
            user_pool_id=user_pool_id, client_id=client_id
        )
        if msg is not None:
            return None, msg

    if client_secret is not None:
        auth_parameters["SECRET_HASH"] = get_secret_hash(
            username, client_id, client_secret
        )

    try:
        resp = client.initiate_auth(
            ClientId=client_id,
            AuthFlow=auth_flow,
            AuthParameters=auth_parameters,
            ClientMetadata=client_metadata,
        )

    except client.exceptions.NotAuthorizedException:
        return None, "Not authorized."
    except client.exceptions.UserNotConfirmedException:
        return None, "User not confirmed."
    except client.exceptions.UserNotFoundException:
        return None, "User not found."
    except client.exceptions.InvalidPasswordException:
        return None, "Invalid password."
    except client.exceptions.InvalidParameterException:
        return None, "Invalid parameter."
    except Exception as e:
        return None, e.__str__()
    return resp, None


ALLOW_ORIGIN = "*"
EXPOSE_HEADERS = "Content-Type"
ALLOW_CREDENTIALS = "true"


def build_response(
    body,
    status_code=200,
):

    resp = dict()
    resp["isBase64Encoded"] = False
    resp["statusCode"] = status_code
    resp["headers"] = dict()
    resp["headers"]["Content-Type"] = "application/json"
    resp["headers"]["Access-Control-Allow-Origin"] = ALLOW_ORIGIN
    resp["headers"]["Access-Control-Expose-Headers"] = EXPOSE_HEADERS

    if status_code != 200:
        resp["headers"]["x-amzn-ErrorType"] = status_code

    resp["body"] = json.dumps(body)
    return resp


"""
class DeveloperMode(object):
    def __init__(self, status = False):
        self.status = status

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            if self.status:
                try:
                    response = func(*args, **kwargs)
                    return response
                except Exception:
                    #response = buildResponse(traceback.format_exc().split('\n'), 502)
                    raise Exception(json.dumps({'message':traceback.format_exc().split('\n')}))
            else:
                return func(*args, **kwargs)
        return wrapper

"""


class Error(Exception):
    pass


class HTTPForbiddenException(Error):
    def __init__(self, message):
        # self.expression = expression
        self.message = message


class HTTPNotFoundException(Error):
    def __init__(self, message):
        # self.expression = expression
        self.message = message


class DeveloperMode(object):
    def __init__(self, status=False):
        self.status = status

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            if self.status:
                try:
                    response = func(*args, **kwargs)
                    return response
                except HTTPNotFoundException as e:
                    print(str(e))
                    return build_response(str(e), 404)
                except HTTPForbiddenException as e:
                    print(str(e))
                    return build_response(str(e), 403)
                except Exception:
                    print(traceback.format_exc().split("\n"))
                    return build_response(traceback.format_exc().split("\n"), 502)
            else:
                return func(*args, **kwargs)

        return wrapper


def get_cognito_username_from_id_token(idToken):
    """
    Get the username from the idToken.

    Args:
        idToken (str): The idToken.

    Returns:
        str: The username.
    """
    try:
        payload = idToken.split(".")[1]
        decode_payload = base64.b64decode(payload + "=" * (-len(payload) % 4))
        payload_dict = json.loads(decode_payload.decode("utf-8"))
        cognito_id = payload_dict["cognito:username"]
        return cognito_id, None
    except Exception as e:
        return None, e.__str__()


def verify_client_id_and_redirect_uri(user_pool_id, client_id, redirect_uri):
    """
    Verify that the client ID and callback URL are valid.

    Args:
        user_pool_id (str): The user pool ID.
        client_id (str): The client ID.
        redirect_uri (str): The callback URL.

    Returns:
        bool: True if the client ID and callback URL are valid.
        str: The error message.
    """
    cognito_client = boto3.client("cognito-idp")
    try:
        resp = cognito_client.describe_user_pool_client(
            UserPoolId=user_pool_id, ClientId=client_id
        )
    except cognito_client.exceptions.ResourceNotFoundException:
        return None, "Client not found."
    except Exception as e:
        return None, e.__str__()
    if redirect_uri not in resp["UserPoolClient"]["CallbackURLs"]:
        return None, "Callback URL not found."
    return resp, None


def store_token_to_dynamodb_and_get_auth_code(
    auth_code_table_name,
    client_id,
    redirect_uri,
    token_set,
):
    """
    Store the token to dynamodb and get the auth code.

    Args:
        client_id (str): The client ID.
        redirect_uri (str): The callback URL.
        token_set (dict): The token set.

    Returns:
        str: The auth code.
        str: The error message.
    """
    dynamodb_client = boto3.client("dynamodb")
    auth_code = str(uuid.uuid4())
    ttl = int(time.time()) + 3600
    code_record = dict()
    code_record["client_id"] = client_id
    code_record["redirect_uri"] = redirect_uri
    code_record["auth_code"] = auth_code
    code_record["ttl"] = ttl
    code_record["token_set"] = json.dumps(token_set)
    while True:
        try:
            dynamodb_client.put_item(
                TableName=auth_code_table_name,
                Item=dynamodb_utils.dumps(code_record, as_dict=True),
                ConditionExpression="attribute_not_exists(auth_code)",
            )
            break
        except dynamodb_client.exceptions.ConditionalCheckFailedException:
            auth_code = str(uuid.uuid4())
            code_record["auth_code"] = auth_code
        except Exception as e:
            return None, e.__str__()
    return auth_code, None


def get_token_from_code(auth_code_table_name, auth_code):
    """
    Get the token from dynamodb.

    Args:
        auth_code_table_name (str): The auth code table name.
        auth_code (str): The auth code.

    Returns:
        dict: The token set.
        str: The error message.
    """
    dynamodb_client = boto3.client("dynamodb")
    try:
        resp = dynamodb_client.get_item(
            TableName=auth_code_table_name,
            Key=dynamodb_utils.dumps({"auth_code": auth_code}, as_dict=True),
        )
    except Exception as e:
        return None, e.__str__()
    if "Item" not in resp:
        return None, "Auth code not found."

    resp_dict = dynamodb_utils.loads(resp["Item"])

    if resp_dict["ttl"] < int(time.time()):
        return None, "Auth code expired."

    token_set = json.loads(resp_dict["token_set"])
    # unvalidate the auth code
    try:
        dynamodb_client.update_item(
            TableName=auth_code_table_name,
            Key=dynamodb_utils.dumps({"auth_code": auth_code}, as_dict=True),
            UpdateExpression="set #ttl_key = :ttl",
            ExpressionAttributeNames={"#ttl_key": "ttl"},
            ExpressionAttributeValues={":ttl": {"N": str(int(time.time()) - 3600)}},
        )
    except Exception as e:
        return None, e.__str__()

    return token_set, None


def verify_client_secret(user_pool_id, client_id, client_secret=None):
    """
    Verify that the client secret is valid.

    Args:
        user_pool_id (str): The user pool ID.
        client_id (str): The client ID.
        client_secret (str): The client secret.

    Returns:
        bool: True if the client secret is valid.
        str: The error message.
    """
    cognito_client = boto3.client("cognito-idp")
    try:
        resp = cognito_client.describe_user_pool_client(
            UserPoolId=user_pool_id, ClientId=client_id
        )
    except cognito_client.exceptions.ResourceNotFoundException:
        return None, "Client not found."
    except Exception as e:
        return None, e.__str__()

    if "ClientSecret" not in resp["UserPoolClient"] and client_secret is None:
        return True, None
    elif "ClientSecret" in resp["UserPoolClient"]:
        if resp["UserPoolClient"]["ClientSecret"] == client_secret:
            return True, None

    return None, "Client secret is not valid."


def get_client_secret(user_pool_id, client_id):
    """
    Get the client secret.

    Args:
        user_pool_id (str): The user pool ID.
        client_id (str): The client ID.

    Returns:
        str: The client secret.
        str: The error message.
    """
    cognito_client = boto3.client("cognito-idp")
    try:
        resp = cognito_client.describe_user_pool_client(
            UserPoolId=user_pool_id, ClientId=client_id
        )
    except cognito_client.exceptions.ResourceNotFoundException:
        return None, "Client not found."
    except Exception as e:
        return None, e.__str__()
    if "ClientSecret" not in resp["UserPoolClient"]:
        return None, None
    return resp["UserPoolClient"]["ClientSecret"], None


def get_client_id_and_secret(authorization):
    """
    Get the client ID and secret.

    Args:
        authorization (str): The authorization header.

    Returns:
        str: The client ID.
        str: The client secret.
        str: The error message.
    """
    if authorization is None:
        return None, None, "Authorization header not found."
    if " " not in authorization:
        return None, None, "Authorization header format error."
    if authorization.split(" ")[0] != "Basic":
        return None, None, "Authorization header format error."
    try:
        client_id_and_secret = base64.b64decode(authorization.split(" ")[1]).decode(
            "utf-8"
        )
    except Exception as e:
        return None, None, e.__str__()
    if ":" not in client_id_and_secret:
        return None, None, "Authorization header format error."
    client_id_and_secret_list = client_id_and_secret.split(":")
    if client_id_and_secret_list[1] == "":
        return client_id_and_secret_list[0], None, None
    return client_id_and_secret_list[0], client_id_and_secret_list[1], None


def format_authentication_result(authentication_result):
    """
    Format the authentication result.

    Args:
        authentication_result (dict): The authentication result.

    Returns:
        dict: The formatted authentication result.
    """
    formatted_authentication_result = dict()
    formatted_authentication_result["access_token"] = authentication_result[
        "AuthenticationResult"
    ]["AccessToken"]
    formatted_authentication_result["id_token"] = authentication_result[
        "AuthenticationResult"
    ]["IdToken"]
    formatted_authentication_result["refresh_token"] = authentication_result[
        "AuthenticationResult"
    ]["RefreshToken"]
    formatted_authentication_result["expires_in"] = authentication_result[
        "AuthenticationResult"
    ]["ExpiresIn"]
    formatted_authentication_result["token_type"] = authentication_result[
        "AuthenticationResult"
    ]["TokenType"]
    return formatted_authentication_result
