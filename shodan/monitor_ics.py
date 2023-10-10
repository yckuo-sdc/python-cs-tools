#!/usr/bin/env python

import os

from dotenv import load_dotenv

from shodan import Shodan
from shodan.cli.helpers import get_api_key

# Configuration
EMAIL_TO = 't910729@gmail.com'
EMAIL_FROM = 'ics-alerts'

load_dotenv()
apikey = os.getenv("SHODAN_NICS_APIKEY")

api = Shodan(apikey)

# Subscribe to results for all networks:
for banner in api.stream.alert():
    # Check whether the banner is from an ICS service
    if 'tags' in banner and 'ics' in banner['tags']:
        send_mail()


def send_mail(subject, content):
    """Send an email using a local mail server."""
    from smtplib import SMTP
    server = SMTP()
    server.connect()
    server.sendmail(EMAIL_FROM, EMAIL_TO,
                    f"Subject: {subject}\n\n{content}")
    server.quit()
