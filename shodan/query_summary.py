from dotenv import load_dotenv
import shodan
import os
import sys
import json

load_dotenv()
apikey = os.environ["shodan_nics_apikey"]

# The list of properties we want summary information on
FACETS = [
    'org',
    'domain',
    'port',
    'asn',

    # We only care about the top 3 countries, this is how we let Shodan know to return 3 instead of the
    # default 5 for a facet. If you want to see more than 5, you could do ('country', 1000) for example
    # to see the top 1,000 countries for a search query.
    ('country', 3),
]

FACET_TITLES = {
    'org': 'Top 5 Organizations',
    'domain': 'Top 5 Domains',
    'port': 'Top 5 Ports',
    'asn': 'Top 5 Autonomous Systems',
    'country': 'Top 3 Countries',
}

try:
    # Setup the api
    api = shodan.Shodan(apikey)
    info = api.info()

    # Perform the search
    #search_filters = {
    #    'country': 'tw', 
    #    'http.html': 'phpmyadmin',
    #    'org': "Government Service Network (GSN)"
    #};
    search_filters = {
        'http.html': 'phpmyadmin',
    };


    query = ' '.join(f'{key}:"{value}"' for key, value in search_filters.items())

    # Use the count() method because it doesn't return results and doesn't require a paid API plan
    # And it also runs faster than doing a search().
    result = api.count(query, facets=FACETS)

    print('Shodan Summary Information')
    print('Query: {}'.format(query))
    print('Total Results: {}'.format(result['total']))

    # Print the summary info from the facets
    for facet in result['facets']:
        print(FACET_TITLES[facet])

        for term in result['facets'][facet]:
            print('{}: {}'.format(term['value'], term['count']))

        # Print an empty line between summary info
        print()

    #result = api.search(query)
    #total = result['total']
    #print('Results found: {}'.format(total))

    #if not total:
    #    raise Exception("No result")

    ## Loop through the matches and print each IP
    #for service in result['matches']:
    #    print(service['ip_str'])
except Exception as e:
    print('Error: %s' % e)
    sys.exit(1)
