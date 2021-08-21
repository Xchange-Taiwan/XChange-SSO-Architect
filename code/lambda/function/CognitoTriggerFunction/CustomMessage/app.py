import json
import base64
import logging

from aws import helper
from aws.helper import DeveloperMode


def apply_email_template(
    display_name: str, description: str, button_label: str, button_link: str
) -> str:
    return (
        """<!doctype html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml"
  xmlns:o="urn:schemas-microsoft-com:office:office">

<head>
  <title>
  </title>
  <!--[if !mso]><!-->
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <!--<![endif]-->
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style type="text/css">
    #outlook a {
      padding: 0;
    }

    body {
      margin: 0;
      padding: 0;
      -webkit-text-size-adjust: 100%;
      -ms-text-size-adjust: 100%;
    }

    table,
    td {
      border-collapse: collapse;
      mso-table-lspace: 0pt;
      mso-table-rspace: 0pt;
    }

    img {
      border: 0;
      height: auto;
      line-height: 100%;
      outline: none;
      text-decoration: none;
      -ms-interpolation-mode: bicubic;
    }

    p {
      display: block;
      margin: 13px 0;
    }
  </style>
  <!--[if mso]>
        <noscript>
        <xml>
        <o:OfficeDocumentSettings>
          <o:AllowPNG/>
          <o:PixelsPerInch>96</o:PixelsPerInch>
        </o:OfficeDocumentSettings>
        </xml>
        </noscript>
        <![endif]-->
  <!--[if lte mso 11]>
        <style type="text/css">
          .mj-outlook-group-fix { width:100% !important; }
        </style>
        <![endif]-->
  <!--[if !mso]><!-->
  <link href="https://fonts.googleapis.com/css?family=Ubuntu:300,400,500,700" rel="stylesheet" type="text/css">
  <style type="text/css">
    @import url(https://fonts.googleapis.com/css?family=Ubuntu:300,400,500,700);
  </style>
  <!--<![endif]-->
  <style type="text/css">
    @media only screen and (min-width:480px) {
      .mj-column-per-100 {
        width: 100% !important;
        max-width: 100%;
      }
    }
  </style>
  <style media="screen and (min-width:480px)">
    .moz-text-html .mj-column-per-100 {
      width: 100% !important;
      max-width: 100%;
    }
  </style>
  <style type="text/css">
    @media only screen and (max-width:480px) {
      table.mj-full-width-mobile {
        width: 100% !important;
      }

      td.mj-full-width-mobile {
        width: auto !important;
      }
    }
  </style>
</head>

<body style="word-spacing:normal; background-color:#ffffff;">
  <div style="background-color:#edf4f7; padding:40px 10px;">
    <!--[if mso | IE]><table align="center" border="0" cellpadding="0" cellspacing="0" class="" style="width:800px;" width="600" bgcolor="#ffffff" ><tr><td style="line-height:0px;font-size:0px;mso-line-height-rule:exactly;"><![endif]-->
    <div style="background:#ffffff;background-color:#ffffff;margin:0px auto;max-width:800px; ">
      <table align="center" border="0" cellpadding="0" cellspacing="0" role="presentation"
        style="background:#ffffff;background-color:#ffffff;width:100%;">
        <tbody>
          <tr>
            <td style="direction:ltr;font-size:0px;padding:0px;text-align:center;">
              <!--[if mso | IE]><table role="presentation" border="0" cellpadding="0" cellspacing="0"><tr><td class="" style="vertical-align:top;width:800px;" ><![endif]-->
              <div class="mj-column-per-100 mj-outlook-group-fix"
                style="font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:100%;">
                <table border="0" cellpadding="0" cellspacing="0" role="presentation" width="100%">
                  <tbody>
                    <tr>
                      <td style="vertical-align:top;padding:0px;">
                        <table border="0" cellpadding="0" cellspacing="0" role="presentation" style width="100%">
                          <tbody>
                            <tr>
                              <td align="center" style="font-size:0px;padding:0px;word-break:break-word;">
                                <table border="0" cellpadding="0" cellspacing="0" role="presentation"
                                  style="border-collapse:collapse;border-spacing:0px;">
                                  <tbody>
                                    <tr>
                                      <td style="width:800px;">
                                        <img alt="header image" height="auto"
                                          src="https://xchange-sso-shared.s3.ap-southeast-1.amazonaws.com/images/mailHeader.png"
                                          style="border:0;display:block;outline:none;text-decoration:none;height:auto;width:100%;font-size:13px;"
                                          width="600">
                                      </td>
                                    </tr>
                                  </tbody>
                                </table>
                              </td>
                            </tr>
                          </tbody>
                        </table>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <!--[if mso | IE]></td></tr></table><![endif]-->
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <!--[if mso | IE]></td></tr></table><table align="center" border="0" cellpadding="0" cellspacing="0" class="" style="width:800px;" width="600" bgcolor="#ffffff" ><tr><td style="line-height:0px;font-size:0px;mso-line-height-rule:exactly;"><![endif]-->
    <div style="background:#003C5A;background-color:#003C5A;margin:0px auto;max-width:800px;">
      <table align="center" border="0" cellpadding="0" cellspacing="0" role="presentation"
        style="background:#003C5A;background-color:#003C5A;width:100%;">
        <tbody>
          <tr>
            <td style="direction:ltr;font-size:0px;padding:0px;padding-bottom:20px;padding-top:10px;text-align:center;">
              <!--[if mso | IE]><table role="presentation" border="0" cellpadding="0" cellspacing="0"><tr><td class="" style="vertical-align:top;width:800px;" ><![endif]-->
              <div class="mj-column-per-100 mj-outlook-group-fix"
                style="font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:100%;">
                <table border="0" cellpadding="0" cellspacing="0" role="presentation" width="100%">
                  <tbody>
                    <tr>
                      <td style="vertical-align:top;padding:0px;">
                        <table border="0" cellpadding="0" cellspacing="0" role="presentation" style width="100%">
                          <tbody>
                            <tr>
                              <td align="center" style="font-size:0px;padding:0 25px 20px 25px;word-break:break-word;">
                                <div
                                  style="font-family:Ubuntu, Helvetica, Arial, sans-serif;font-size:20px;line-height:1.5;text-align:center;color:#b3d9e6;">
                                  <strong>Hey """
        + str(display_name)
        + """!</strong>
                                </div>
                              </td>
                            </tr>
                            <tr>
                              <td align="center" style="font-size:0px;padding:0 25px;word-break:break-word;">
                                <div
                                  style="font-family:Arial;font-size:16px;line-height:1.5;text-align:center;color:#ffffff;">
                                  Welcome to XChange<br>"""
        + str(description)
        + """</div>
                              </td>
                            </tr>
                            <tr>
                              <td align="center" vertical-align="middle"
                                style="font-size:0px;padding:20px 0 0 0;word-break:break-word;">
                                <table border="0" cellpadding="0" cellspacing="0" role="presentation"
                                  style="border-collapse:separate;line-height:100%;">
                                  <tr>
                                    <td align="center" bgcolor="#009690" role="presentation"
                                      style="border:none;border-radius:80px;cursor:auto;mso-padding-alt:10px 25px;background: #009690;"
                                      valign="middle">
                                      <a style="display: inline-block; background: #009690; font-family: Arial, sans-serif; font-size: 16px; font-weight: bold; line-height: 120%; margin: 0; text-transform: none; padding: 10px 25px; mso-padding-alt: 0px; border-radius: 3px; text-decoration: none; color: #ffffff;"
                                        target="_blank" href=\""""
        + str(button_link)
        + """">"""
        + str(button_label)
        + """</a>
                                    </td>
                                  </tr>
                                </table>
                              </td>
                            </tr>
                            <tr>
                              <td align="center"
                                style="font-size:0px;padding:0 25px;padding-top:40px;word-break:break-word;">
                                <div
                                  style="font-family:Arial, sans-serif;font-size:14px;line-height:1.5;text-align:center;color:#b3d9e6;">
                                  Best, <br> XChange Team <p></p>
                                </div>
                              </td>
                            </tr>
                          </tbody>
                        </table>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <!--[if mso | IE]></td></tr></table><![endif]-->
            </td>
          </tr>
        </tbody>
      </table>
      <table align="center" border="0" cellpadding="0" cellspacing="0" role="presentation"
        style="background:#005780; width:100%;">
        <tbody>
          <tr>
            <td align="center" style="font-size:0px;padding: 20px 10px 10px 10px;word-break:break-word;">
              <!--[if mso | IE]><table align="center" border="0" cellpadding="0" cellspacing="0" role="presentation" ><tr><td><![endif]-->
              <table align="center" border="0" cellpadding="0" cellspacing="0" role="presentation"
                style="float:none;display:inline-table;">
                <tbody>
                  <tr>
                    <td style="padding:8px;vertical-align:middle;">
                      <table border="0" cellpadding="0" cellspacing="0" role="presentation"
                        style="background:#3b5998;border-radius:80px;width:30px;">
                        <tbody>
                          <tr>
                            <td style="font-size:0;height:30px;vertical-align:middle;width:30px;">
                              <a href="https://www.facebook.com/groups/811949022260117" target="_blank">
                                <img height="30"
                                  src="https://xchange-sso-shared.s3.ap-southeast-1.amazonaws.com/images/facebook.png"
                                  style="border-radius:80px;display:block;box-shadow: 0 0 3px rgb(20 66 86);"
                                  width="30"></a>
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </td>
                  </tr>
                </tbody>
              </table>
              <!--[if mso | IE]></td><td><![endif]-->
              <table align="center" border="0" cellpadding="0" cellspacing="0" role="presentation"
                style="float:none;display:inline-table;">
                <tbody>
                  <tr>
                    <td style="padding:8px;vertical-align:middle;">
                      <table border="0" cellpadding="0" cellspacing="0" role="presentation"
                        style="background:#0d65c2;border-radius:80px;width:30px;">
                        <tbody>
                          <tr>
                            <td style="font-size:0;height:30px;vertical-align:middle;width:30px;">
                              <a href="https://www.linkedin.com/company/xchange-tw/" target="_blank">
                                <img height="30"
                                  src="https://xchange-sso-shared.s3.ap-southeast-1.amazonaws.com/images/linkedin.png"
                                  style="border-radius:80px;display:block;box-shadow: 0 0 3px rgb(20 66 86);"
                                  width="30"></a>
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </td>
                  </tr>
                </tbody>
              </table>
              <!--[if mso | IE]></td><td><![endif]-->
              <table align="center" border="0" cellpadding="0" cellspacing="0" role="presentation"
                style="float:none;display:inline-table;">
                <tbody>
                  <tr>
                    <td style="padding:8px;vertical-align:middle;">
                      <table border="0" cellpadding="0" cellspacing="0" role="presentation"
                        style="background:#3f729b;border-radius:80px;width:30px;">
                        <tbody>
                          <tr>
                            <td style="font-size:0;height:30px;vertical-align:middle;width:30px;">
                              <a href="https://www.instagram.com/xchange.tw/" target="_blank">
                                <img height="30"
                                  src="https://xchange-sso-shared.s3.ap-southeast-1.amazonaws.com/images/instagram.png"
                                  style="border-radius:80px;display:block;box-shadow: 0 0 3px rgb(20 66 86);"
                                  width="30"></a>
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </td>
                  </tr>
                </tbody>
              </table>
              <!--[if mso | IE]></td><td><![endif]-->
              <table align="center" border="0" cellpadding="0" cellspacing="0" role="presentation"
                style="float:none;display:inline-table;">
                <tbody>
                  <tr>
                    <td style="padding:8px;vertical-align:middle;">
                      <table border="0" cellpadding="0" cellspacing="0" role="presentation"
                        style="background:#000000;border-radius:80px;width:30px;">
                        <tbody>
                          <tr>
                            <td style="font-size:0;height:30px;vertical-align:middle;width:30px;">
                              <a href="https://xchange-taiwan.medium.com/" target="_blank">
                                <img height="30"
                                  src="https://xchange-sso-shared.s3.ap-southeast-1.amazonaws.com/images/medium.png"
                                  style="border-radius:80px;display:block;box-shadow: 0 0 3px rgb(20 66 86);"
                                  width="30"></a>
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </td>
                  </tr>
                </tbody>
              </table>
              <!--[if mso | IE]></td></tr></table><![endif]-->
            </td>
          </tr>
          <tr>
            <td align="center" style="font-size:0px;padding:15px 10px 0px 10px;word-break:break-word;">
              <table border="0" cellpadding="0" cellspacing="0" role="presentation"
                style="border-collapse:collapse;border-spacing:0px;">
                <tbody>
                  <tr>
                    <td style="width:80px;">
                      <img height="auto"
                        src="https://xchange-sso-shared.s3.ap-southeast-1.amazonaws.com/images/XChangeLogo_White.png"
                        style="border:0;display:block;outline:none;text-decoration:none;height:auto;width:100%;font-size:13px;"
                        width="202">
                    </td>
                  </tr>
                </tbody>
              </table>
            </td>
          </tr>
          <tr>
            <td align="center" style="font-size:0px;padding:10px 10px 30px 10px;word-break:break-word;">
              <table border="0" cellpadding="0" cellspacing="0" role="presentation"
                style="border-collapse:collapse;border-spacing:0px;">
                <tbody>
                  <tr>
                    <td>
                      <div
                        style="font-family:Arial, sans-serif;font-size:11px;line-height:1.5;text-align:center;color:#b3d9e6;">
                        Copyright © 2021 XChange, All rights reserved.</div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </td>
          </tr>
        </tbody>
      </table>

    </div>
    <!--[if mso | IE]></td></tr></table><![endif]-->
  </div>
</body>

</html>
"""
    )


@DeveloperMode(True)
def lambda_handler(event, context):

    email = event["request"]["userAttributes"]["email"]
    cognitoUsername = event["userName"]
    cognitoClientID = event["callerContext"]["clientId"]
    triggerSource = event["triggerSource"]
    host = "https://sso.xchange.com.tw"
    # host = "http://localhost:4200"

    emailSubject = ""
    emailMessage = ""

    responseState = None

    if (
        "clientMetadata" in event["request"]
        and not event["request"]["clientMetadata"] is None
    ):
        responseState = event["request"]["clientMetadata"]

    responseStateHash = None

    if not responseState is None:
        responseStateHash = base64.b64encode(
            json.dumps(responseState).encode("utf-8")
        ).decode("utf-8")

    if triggerSource == "CustomMessage_ForgotPassword":
        emailSubject = "XChange - Reset Password"
        email_link = (
            host
            + """/reset-password/?code={####}&email="""
            + email
            + ("&state=" + responseStateHash)
            if responseStateHash
            else ""
        )
        emailMessage = apply_email_template(
            display_name=email,
            description="Click the link below to continue the password reset process.",
            button_label="Reset Password",
            button_link=email_link,
        )
    elif (
        triggerSource == "CustomMessage_ResendCode"
        or triggerSource == "CustomMessage_SignUp"
    ):
        emailSubject = "XChange - Confirm Account"
        email_link = (
            host
            + """/confirm-email/?code={####}&email="""
            + email
            + ("&state=" + responseStateHash)
            if responseStateHash
            else ""
        )
        emailMessage = apply_email_template(
            display_name=email,
            description="Please Verify your email",
            button_label="Verify",
            button_link=email_link,
        )
    else:
        logging.info("unhandled trigger")

    event["response"]["emailMessage"] = emailMessage
    event["response"]["emailSubject"] = emailSubject
    return event
