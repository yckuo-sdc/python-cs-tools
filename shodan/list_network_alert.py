import os

from dotenv import load_dotenv

import shodan

load_dotenv()
apikey = os.getenv("SHODAN_NICS_APIKEY")

# Create a Shodan API client
api = shodan.Shodan(apikey)

try:
    # Create the network alert
    alert = api.alerts()
    print(alert)

except shodan.APIError as e:
    print(f"Error: {e}")
