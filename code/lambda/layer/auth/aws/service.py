import json
import boto3
from botocore.exceptions import ClientError
import base64


def sendSQSMessage(sqsQueueURL, body):
    """

    :param sqsQueueURL: String URL of existing SQS queue
    :param body: String message body
    :return: Dictionary containing information about the sent message. If
        error, returns None.
    """

    # Send the SQS message
    sqs_client = boto3.client("sqs")
    try:
        msg = sqs_client.send_message(QueueUrl=sqsQueueURL, MessageBody=body)
    except ClientError as e:
        # logging.error(e)
        return None
    return msg


def getSecret(secretName, regionName="ap-southeast-1"):
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name="secretsmanager", region_name=regionName)

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secretName)
        print(get_secret_value_response)
    except ClientError as e:
        if e.response["Error"]["Code"] == "DecryptionFailureException":
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "InternalServiceErrorException":
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "InvalidParameterException":
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "InvalidRequestException":
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "ResourceNotFoundException":
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if "SecretString" in get_secret_value_response:
            secret = get_secret_value_response["SecretString"]
        else:
            decoded_binary_secret = base64.b64decode(
                get_secret_value_response["SecretBinary"]
            )
    try:
        json_secret = json.loads(secret)
        secret = json_secret
    except Exception as e:
        pass
    return secret


def sendEmail(
    sender, recipient, subject, body, bodyHtml, awsRegion="us-west-2", charset="UTF-8"
):
    SENDER = sender
    RECIPIENT = recipient
    AWS_REGION = awsRegion
    CHARSET = charset  # The character encoding for the email.
    SUBJECT = subject  # The subject line for the email.
    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = body
    BODY_HTML = bodyHtml  # The HTML body of the email.

    # Create a new SES resource and specify a region.
    client = boto3.client("ses", region_name=AWS_REGION)
    # Try to send the email.
    try:
        # Provide the contents of the email.
        response = client.send_email(
            Destination={
                "ToAddresses": [
                    RECIPIENT,
                ],
            },
            Message={
                "Body": {
                    "Html": {
                        "Charset": CHARSET,
                        "Data": BODY_HTML,
                    },
                    "Text": {
                        "Charset": CHARSET,
                        "Data": BODY_TEXT,
                    },
                },
                "Subject": {
                    "Charset": CHARSET,
                    "Data": SUBJECT,
                },
            },
            Source=SENDER,
        )
    except ClientError as e:
        return e.response["Error"]["Message"]
    else:
        return 1
