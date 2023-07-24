from shodan import Shodan
import configparser
import os
import json

config = configparser.ConfigParser()
config.read(os.path.dirname(__file__) + '/../config.ini', encoding='utf-8')
apikey = config['shodan']['nics_apikey']
api = Shodan(apikey)

## Lookup an IP
ipinfo = api.host('8.8.8.8')
jsonStr = json.dumps(ipinfo, indent=1)
print(jsonStr)

## Search for websites that have been "hacked"
#for banner in api.search_cursor('http.title:"hacked by"'):
#    print(banner)

# Get the total number of industrial control systems services on the Internet
ics_services = api.count('tag:ics')
print('Industrial Control Systems: {}'.format(ics_services['total']))

