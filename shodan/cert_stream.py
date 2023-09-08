import json
import os
import sys

from dotenv import load_dotenv

import shodan

load_dotenv()
apikey = os.getenv("SHODAN_NICS_APIKEY")

try:
    # Setup the api
    api = shodan.Shodan(apikey)
    info = api.info()
    print(info)

    print('Listening for certs...')
    for banner in api.stream.ports([443, 8443]):
        if 'ssl' in banner:
            # Print out all the SSL information that Shodan has collected
            print(banner['ssl'])

except Exception as e:
    print('Error: %s' % e)
    sys.exit(1)
