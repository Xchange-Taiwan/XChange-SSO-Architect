import json


def lambda_handler(event, context):
    if event["triggerSource"] == "DefineAuthChallenge_Authentication":
        event["response"]["challengeName"] = "CUSTOM_CHALLENGE"
        event["response"]["issueTokens"] = True
        event["response"]["failAuthentication"] = False

        if event["request"]["session"]:  # Needed for step 4.
            # If all of the challenges are answered, issue tokens.
            event["response"]["issueTokens"] = all(
                answered_challenge["challengeResult"]
                for answered_challenge in event["request"]["session"]
            )
    return event
