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

    def basic_query(self,
                    search_filters,
                    match_fields,
                    retrieve_all_pages=False):
        """Method printing python version."""
        try:
            if isinstance(search_filters, dict):
                query = ' '.join(f'{key}:"{value}"'
                                 for key, value in search_filters.items()
                                 if key != 'all_no_quotes')
                query = query.replace('all:', '')
                if 'all_no_quotes' in search_filters:
                    query = f'{query} {search_filters["all_no_quotes"]}'
            else:
                query = search_filters

            print(f'Query: {query}')
            result = self.__api.search(query)
            total = result['total']
            print(f"Results found: {total}")

            results = []
            if not retrieve_all_pages:
                results = result['matches']
            else:
                page = 1
                print("Paginate search results...")
                while True:
                    response = self.__api.search(query, page=page)
                    results.extend(response['matches'])
                    page_total = len(response['matches'])
                    print(len(results), page_total, page)

                    if page_total == 0:
                        break
                    page = page + 1

            matches = []
            ## Loop through the matches and print each IP
            for result in results:
                match = {}
                for match_field in match_fields:
                    match[match_field['label']] = result.get(
                            match_field['field'])

                matches.append(match)

            return matches

        except Exception as e:
            print(f"Error: {e}")
            return False

    def basic_query_cursor(self, search_filters, match_fields):
        """Method printing python version."""
        try:
            if isinstance(search_filters, dict):
                query = ' '.join(f'{key}:"{value}"'
                                 for key, value in search_filters.items()
                                 if key != 'all_no_quotes')
                query = query.replace('all:', '')
                if 'all_no_quotes' in search_filters:
                    query = f'{query} {search_filters["all_no_quotes"]}'
            else:
                query = search_filters

            print(f'Query: {query}')
            banners = self.__api.search_cursor(query)

            matches = []
            ## Loop through the matches and print each IP
            for banner in banners:
                match = {}
                for match_field in match_fields:
                    if isinstance(match_field['field'], dict):
                        items = match_field['field'].items()
                        item = next(iter(items), None)
                        match[match_field['label']] = banner.get(
                                item[0], {}).get(item[1])
                    else:
                        match[match_field['label']] = banner.get(
                                match_field['field'])

                matches.append(match)

            print(f"Results found: {len(matches)}")
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
        {
            'label': 'ip',
            'field': 'ip_str'
        },
        {
            'label': 'port',
            'field': 'port'
        },
    ]

    r = sa.basic_query(search_filters, match_fields)
    print(r)