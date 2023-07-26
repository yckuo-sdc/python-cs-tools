from dotenv import load_dotenv
import shodan
import os
import sys
import json

load_dotenv()
apikey = os.getenv("SHODAN_NICS_APIKEY")


try:
    # Setup the api
    api = shodan.Shodan(apikey)
    info = api.info()
    #print(info)


    # Perform the search
    search_filters = {
        'country': 'tw', 
        'http.html': 'phpmyadmin',
        'org': "Government Service Network (GSN)"
    };

    query = ' '.join(f'{key}:"{value}"' for key, value in search_filters.items())
    print('Query: {}'.format(query))

    result = api.search(query)
    total = result['total']
    print('Results found: {}'.format(total))

    #if not total:
    #    raise Exception("No result")

    ## Loop through the matches and print each IP
    #for service in result['matches']:
    #    print(service['ip_str'])
except Exception as e:
    print('Error: %s' % e)
    sys.exit(1)
