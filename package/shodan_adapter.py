import os

import shodan
from dotenv import load_dotenv


class ShodanAdapter:
    __api = None

    def __init__(self, api=""):
        if api == "":
            load_dotenv()
            apikey = os.getenv("SHODAN_NICS_APIKEY")
            self.__api = shodan.Shodan(apikey)
        else:
            self.__api = api

    def basic_query(self, search_filters, match_fields):
        """Method printing python version."""
        try:
            #info = self.__api.info()

            # Perform the search
            query = ' '.join(f'{key}:"{value}"'
                             for key, value in search_filters.items())
            query = query.replace('all:', '')
            print(f'Query: {query}')

            result = self.__api.search(query)
            total = result['total']
            print(f"Results found: {total}")

            #if not total:
            #    raise Exception("No result")

            #print(result['matches'])
            matches = []
            ## Loop through the matches and print each IP
            for result in result['matches']:
                match = {}
                for match_field in match_fields:
                    match[match_field['label']] = result.get(match_field['field'])

                matches.append(match)

            return matches

        except Exception as e:
            print(f"Error: {e}")
            return False


if __name__ == '__main__':
    sa = ShodanAdapter()

    search_filters = {
        'country': 'tw',
        'org': "Government Service Network (GSN)",
        'all': 'ldap',
    }

    match_fields = [
        {'label': 'ip', 'field': 'ip_str'},
        {'label': 'port', 'field': 'port'},
    ]

    r = sa.basic_query(search_filters, match_fields)
    print(r)
