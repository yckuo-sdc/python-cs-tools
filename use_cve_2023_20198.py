"""Module Proof of Concept for CVE-2018-17020."""
import os

import datetime

import pandas as pd
import requests

from package.ip2gov_adapter import Ip2govAdapter
from package.shodan_adapter import ShodanAdapter

ACCESSIBLE_CODES = [200]


def get_response_code(url):
    try:
        headers = {
            'user-agent':
            'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/115.0.0.0 safari/537.36'
        }
        # ignore verifying the ssl certificate
        response = requests.get(url,
                                headers=headers,
                                allow_redirects=True,
                                verify=False,
                                timeout=5)
        return response.status_code
    except Exception as e:
        print(e)
        return False


def is_hexadecimal_string(input_string):
    """Function confirm that web page is accessible."""
    # Check if the input string is not empty
    if len(input_string) == 0:
        return False

    # Check if the input string contains only hexadecimal characters (0-9, a-f, A-F)
    return all(
        char.isalnum() and char.isnumeric() or 'a' <= char.lower() <= 'f'
        for char in input_string)


def is_accessible(request_url):
    """Function confirm that web page is accessible."""
    code = get_response_code(request_url)
    if code not in ACCESSIBLE_CODES:
        return False

    return True


def is_implanted(request_url):
    """Function confirm that web page is implanted."""

    try:
        headers = {
            'user-agent':
            'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/115.0.0.0 safari/537.36'
        }
        path = '/webui/logoutconfirm.html'
        query = 'logon_hash=1'
        test_url = f"{request_url}{path}?{query}"
        print(test_url)
        # ignore verifying the ssl certificate
        response = requests.post(test_url,
                                 headers=headers,
                                 allow_redirects=False,
                                 verify=False,
                                 timeout=5)
        string = response.text.strip()
        if is_hexadecimal_string(string):
            return string

        return False
        #return is_hexadecimal_string(string)
    except Exception as e:
        print(e)
        return False


if __name__ == '__main__':

    ip2gov = Ip2govAdapter()
    sa = ShodanAdapter()

    #print(is_implanted('https://163.29.251.185'))
    #print(is_implanted('http://61.60.10.65'))
    #print(is_implanted('https://210.241.73.127:443'))
    #input('press')

    #search_filters = {
    #    'asn': 'AS4782',
    #    'all_no_quotes': 'server: openresty',
    #}

    search_filters = {
        'asn': 'AS4782',
        'http.html': 'webui',
        'product': 'OpenResty,nginx',
    }

    match_fields = [{
        'label': 'ip',
        'field': 'ip_str'
    }, {
        'label': 'port',
        'field': 'port'
    }, {
        'label': 'product',
        'field': 'product'
    }, {
        'label': 'ssl',
        'field': 'ssl'
    }]

    fields = sa.basic_query_cursor(search_filters, match_fields)
    print(fields)

    output = []
    for field in fields:
        EXPOSED = False
        #IMPLANTED = False
        HEX_STR = False
        DEP = None
        CLASS = None
        ACC = None

        host = field['ip']
        port = field['port']

        if field['ssl'] is None:
            field['ssl'] = False
            url = f"http://{host}:{port}"
        else:
            field['ssl'] = True
            url = f"https://{host}:{port}"

        field['url'] = url
        print(host, port, url)

        #gov_data = ip2gov.get_gov_data_by_ip(field['ip'])
        #if gov_data:
        #    DEP = gov_data.get('DEP')
        #    CLASS = gov_data.get('Class')
        #    ACC = gov_data.get('ACC')

        EXPOSED = is_accessible(url)
        #IMPLANTED = is_implanted(url)
        HEX_STR = is_implanted(url)
        current_time = datetime.datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

        output.append(
                field | \
                {'dep': DEP} | \
                {'acc': ACC} | \
                {'class': CLASS} | \
                {'exposed': EXPOSED} | \
                #{'implanted': IMPLANTED}
                {'hex string': HEX_STR} |
                {'timestamp': formatted_time}
        )

    df = pd.DataFrame(output)
    path_to_csv = os.path.join(os.path.dirname(__file__), "data",
                               "use_cve_2023_20198.csv")
    df.to_csv(path_to_csv, index=False, encoding='utf-8-sig')
