import boto3
import botocore.exceptions
import base64
import json
import hmac
import hashlib
import traceback

import re


class Helper:
    EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")


def representsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def cognitoAuthorizer(event):
    claims = event["requestContext"]["authorizer"]["claims"]
    return claims


def getSecretHash(username, clientID, clientSecret):
    msg = username + clientID
    dig = hmac.new(
        str(clientSecret).encode("utf-8"),
        msg=str(msg).encode("utf-8"),
        digestmod=hashlib.sha256,
    ).digest()
    d2 = base64.b64encode(dig).decode()
    return d2


def deleteUser(userPoolID, username):
    client = boto3.client("cognito-idp")
    try:
        resp = client.admin_delete_user(
            UserPoolId=userPoolID, Username=username)
    except Exception as e:
        return None, e.__str__()

    return resp, None


def getUser(userPoolID, username):
    client = boto3.client("cognito-idp")
    try:
        resp = client.admin_get_user(UserPoolId=userPoolID, Username=username)
    except Exception as e:
        return None, e.__str__()

    return resp, None


def adminCreateUser(userPoolID, email, password):
    client = boto3.client("cognito-idp")

    try:
        resp = client.admin_create_user(
            UserPoolId=userPoolID,
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
            UserPoolId=userPoolID,
            Username=cognitoUsername,
            Password=password,
            Permanent=True,
        )
    except Exception as e:
        print("Exception - Other Password Set")
        print(e.__str__())

    return resp, None


def adminConfirmSignUp(
    userPoolID,
    username,
    email=None,
    clientID=None,
    clientSecret=None,
    clientMetadata=dict(),
):
    client = boto3.client("cognito-idp")

    if not clientSecret is None:
        secretHash = getSecretHash(username, clientID, clientSecret)

    try:
        if not clientSecret is None:
            resp = client.admin_confirm_sign_up(
                UserPoolId=userPoolID,
                Username=username,
            )
        else:
            resp = client.admin_confirm_sign_up(
                UserPoolId=userPoolID,
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


def confirmSignUp(
    username, email, code, clientID, clientSecret=None, clientMetadata=dict()
):
    client = boto3.client("cognito-idp")

    if not clientSecret is None:
        secretHash = getSecretHash(username, clientID, clientSecret)

    try:
        resp = client.confirm_sign_up(
            ClientId=clientID,
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


def confirmForgotPassword(
    username, email, password, code, clientID, clientSecret=None, clientMetadata=dict()
):
    client = boto3.client("cognito-idp")

    if not clientSecret is None:
        secretHash = getSecretHash(username, clientID, clientSecret)

    try:
        resp = client.confirm_forgot_password(
            ClientId=clientID,
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
    userPoolID,
    username,
    email,
    password,
    clientID,
    clientSecret=None,
    clientMetadata=dict(),
):
    client = boto3.client("cognito-idp")
    userAttributes = list()
    userAttribute = dict()
    userAttribute["Name"] = "email"
    userAttribute["Value"] = email

    userAttributes.append(userAttribute)

    if not clientSecret is None:
        secretHash = getSecretHash(username, clientID, clientSecret)

    try:
        if not clientSecret is None:
            resp = client.sign_up(
                ClientId=clientID,
                SecretHash=secretHash,
                Username=email,
                Password=password,
                UserAttributes=userAttributes,
                ClientMetadata=clientMetadata,
            )
        else:
            resp = client.sign_up(
                ClientId=clientID,
                Username=email,
                Password=password,
                UserAttributes=userAttributes,
                ClientMetadata=clientMetadata,
            )

    except client.exceptions.UsernameExistsException as e:
        return None, "Username exists."
    except client.exceptions.InvalidPasswordException as e:
        return None, "Invalid password."
    except client.exceptions.UserLambdaValidationException as e:
        return None, "User lambda validation."
    except Exception as e:
        return None, e.__str__()

    return resp, None


def resendConfirm(username, clientID, clientSecret=None, clientMetadata=dict()):
    client = boto3.client("cognito-idp")

    if not clientSecret is None:
        secretHash = getSecretHash(username, clientID, clientSecret)

    try:
        resp = client.resend_confirmation_code(
            ClientId=clientID, Username=username, ClientMetadata=clientMetadata
        )

    except client.exceptions.UserNotFoundException:
        return None, "User not found."
    except client.exceptions.InvalidParameterException:
        return None, "Invalid parameter."
    except Exception as e:
        return None, e.__str__()

    return resp, None


def forgotPassword(username, clientID, clientSecret=None, clientMetadata=dict()):
    client = boto3.client("cognito-idp")

    if not clientSecret is None:
        secretHash = getSecretHash(username, clientID, clientSecret)

    try:
        resp = client.forgot_password(
            ClientId=clientID, Username=username, ClientMetadata=clientMetadata
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


# def refreshAuth(userPoolID, username, refreshToken, clientID, clientSecret):
def refreshAuth(username, refreshToken, clientID, clientSecret=None):
    client = boto3.client("cognito-idp")

    authParameters = dict()
    authParameters["REFRESH_TOKEN"] = refreshToken

    if not clientSecret is None:
        authParameters["SECRET_HASH"] = getSecretHash(
            username, clientID, clientSecret)

    try:
        resp = client.initiate_auth(
            ClientId=clientID,
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


def initiateAuth(
    userPoolID,
    username,
    password,
    clientID,
    clientSecret=None,
    authFlow="USER_PASSWORD_AUTH",
):
    client = boto3.client("cognito-idp")

    authParameters = dict()
    clientMetadata = dict()

    authParameters["USERNAME"] = username
    clientMetadata["username"] = username
    authParameters["PASSWORD"] = password
    clientMetadata["password"] = password

    # Client credential
    if authFlow == "ADMIN_NO_SRP_AUTH":
        authParameters["PASSWORD"] = password
        clientMetadata["password"] = password

    # Challenge flow
    elif authFlow == "CUSTOM_AUTH":
        pass

    if clientSecret is not None:
        authParameters["SECRET_HASH"] = getSecretHash(
            username, clientID, clientSecret)

    try:
        # if authFlow == "USER_PASSWORD_AUTH":
        resp = client.initiate_auth(
            ClientId=clientID,
            AuthFlow=authFlow,
            AuthParameters=authParameters,
            ClientMetadata=clientMetadata,
        )
        # else:
        #     resp = client.admin_initiate_auth(
        #         UserPoolId=userPoolID,
        #         ClientId=clientID,
        #         AuthFlow=authFlow,
        #         AuthParameters=authParameters,
        #         ClientMetadata=clientMetadata,
        #     )

    except client.exceptions.NotAuthorizedException:
        return None, "Not authorized."
    except client.exceptions.UserNotConfirmedException:
        return None, "User not found."
    except Exception as e:
        return None, e.__str__()

    return resp, None


ALLOW_ORIGIN = "*"
EXPOSE_HEADERS = "Content-Type"
ALLOW_CREDENTIALS = "true"


def buildResponse(
    body,
    statusCode=200,
):

    resp = dict()
    resp["isBase64Encoded"] = False
    resp["statusCode"] = statusCode
    resp["headers"] = dict()
    resp["headers"]["Content-Type"] = "application/json"
    resp["headers"]["Access-Control-Allow-Origin"] = ALLOW_ORIGIN
    resp["headers"]["Access-Control-Expose-Headers"] = EXPOSE_HEADERS

    if statusCode != 200:
        resp["headers"]["x-amzn-ErrorType"] = statusCode

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
                    return buildResponse(str(e), 404)
                except HTTPForbiddenException as e:
                    print(str(e))
                    return buildResponse(str(e), 403)
                except Exception:
                    print(traceback.format_exc().split("\n"))
                    return buildResponse(traceback.format_exc().split("\n"), 502)
            else:
                return func(*args, **kwargs)

        return wrapper
