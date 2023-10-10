import os

from dotenv import load_dotenv

import shodan

load_dotenv()
apikey = os.getenv("SHODAN_NICS_APIKEY")

# Create a Shodan API client
api = shodan.Shodan(apikey)

# Define the alert parameters
alert_name = "ICS Network Alert"
ip = "223.200.123.68"  # Define your search query

try:
    # Create the network alert
    alert = api.create_alert(alert_name, ip)

    # Print the alert information
    print(f"Alert ID: {alert['id']}")
    print(f"Name: {alert['name']}")
    print(f"Query: {alert['filters']['query']}")
except shodan.APIError as e:
    print(f"Error: {e}")
