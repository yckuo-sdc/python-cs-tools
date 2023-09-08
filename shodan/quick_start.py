import configparser
import json
import os

from dotenv import load_dotenv

from shodan import Shodan

load_dotenv()
api = Shodan(os.getenv("SHODAN_NICS_APIKEY"))

### Lookup an IP
#ipinfo = api.host('8.8.8.8')
#jsonStr = json.dumps(ipinfo, indent=1)
#print(jsonStr)
#
### Search for websites that have been "hacked"
##for banner in api.search_cursor('http.title:"hacked by"'):
##    print(banner)
#
## Get the total number of industrial control systems services on the Internet
#ics_services = api.count('tag:ics')
#print('Industrial Control Systems: {}'.format(ics_services['total']))


# Wrap the request in a try/ except block to catch errors
try:
    # Search Shodan
    results = api.search('apache')
    print(json.dumps(results, indent=1))
    
    # Show the results
    #print('Results found: {}'.format(results['total']))
    #for result in results['matches']:
    #    print('IP: {}'.format(result['ip_str']))
    #    print(result['data'])
    #    print('')
except (shodan.APIError, e):
    print('Error: {}'.format(e))
