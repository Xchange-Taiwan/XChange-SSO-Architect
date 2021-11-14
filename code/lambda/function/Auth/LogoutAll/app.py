from aws import helper
from aws.helper import DeveloperMode


@DeveloperMode(True)
def lambda_handler(event, context):
    # return helper.buildResponse(event)
    # account = Account.getWithJWTToken(event['headers']['authorization'])
    return helper.build_response(event)
