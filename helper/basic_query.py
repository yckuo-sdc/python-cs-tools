import json
import os
import sys

from dotenv import load_dotenv

import shodan

load_dotenv()
apikey = os.getenv("SHODAN_NICS_APIKEY")

def basic_query(search_filters):
    try:
        # Setup the api
        api = shodan.Shodan(apikey)
        info = api.info()
        #print(info)


        # Perform the search
        query = ' '.join(f'{key}:"{value}"' for key, value in search_filters.items())   
        query = query.replace('all:', '')
        
        #query = query + ""'
        print('Query: {}'.format(query))

        result = api.search(query)
        total = result['total']
        print('Results found: {}'.format(total))

        #if not total:
        #    raise Exception("No result")

        #print(result['matches'])
        services = []
        ## Loop through the matches and print each IP
        for result in result['matches']:
            services.append({'ip': result['ip_str'], 'port': result['port']})

        return services 

    except Exception as e:
        print('Error: %s' % e)
        return False

if __name__ == '__main__':  
    search_filters = {
        'country': 'tw', 
        'org': "Government Service Network (GSN)",
        'all': 'ldap',
    };
    r = basic_query(search_filters)
    print(r)


