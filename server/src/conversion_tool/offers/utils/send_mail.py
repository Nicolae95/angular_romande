# -*- coding: utf-8 -*-
# from __future__ import unicode_literals
import smtplib
import os
from os.path import basename
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email.MIMEBase import MIMEBase
from email import encoders
from django.conf import settings


def py_mail(SUBJECT, BODY, files, TO, FROM):
    """With this function we send out our html email"""
    # Create message container - the correct MIME type is multipart/alternative here!
    MESSAGE = MIMEMultipart('mixed')
    MESSAGE['subject'] = SUBJECT
    MESSAGE['To'] = TO
    MESSAGE['From'] = FROM
    MESSAGE.preamble = """
        Your mail reader does not support the report format.
        Please visit us <a href="/">online</a>!"""
    # Record the MIME type text/html.
    HTML_BODY = MIMEText(BODY.encode('utf-8'), 'html', 'utf-8')
    MESSAGE.attach(HTML_BODY)

    for filename in files:
        if filename != '':
            attachment = open(filename, "rb")
            part = MIMEBase('application', 'octet-stream')
            part.set_payload((attachment).read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(filename).encode('utf8'))
            MESSAGE.attach(part)

    # The actual sending of the e-mail
    # server = smtplib.SMTP('smtp.gmail.com:587')
    server = smtplib.SMTP(getattr(settings, 'MAIL_SERVER'))

    # Print debugging output when testing
    if __name__ == "__main__":
        server.set_debuglevel(1)

    # Credentials (if needed) for sending the mail
    # password = "energymarketprice"
    password = getattr(settings, 'MAIL_PASSWORD')

    server.starttls()
    if password:
        server.login(FROM,password)
    server.sendmail(FROM, [TO], MESSAGE.as_string())
    server.quit()

if __name__ == "__main__":
    """Executes if the script is run as main script (for testing purposes)"""

    email_content = """
        <head>
          <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
              <title>Title</title>
          <style type="text/css" media="screen">
            table{
                empty-cells:hide;
            }
            td.cell{
                background-color: white;
                border-right: 1px solid;
            }
          </style>
        </head>
        <body>
          <table align="center" style="border:1px solid #fff;width: 758px;">
            <tr><td class="cell"><img src="https://i.imgur.com/BZhaRTq.png"></td></tr>
            <tr><td align="center" style="background-color: #e0b20a;font-size: 26px;color:#fff;height:20px;border-right:1px solid;padding: 17px;">VOIR RAPPORT CUSTOMISE    ></td></tr>
            <tr><td align="center" class="cell"><img src="https://i.imgur.com/g8LfdYa.png"></td></tr>
          </table>
        </body>
    """

    TO = 'nicolae.botnaru@gmail.com'
    FROM = 'non.commodity.data@gmail.com'
    # FROM = 'nicolae.botnaru@gmail.com'

    py_mail("Test email subject", email_content, [], TO, FROM)
