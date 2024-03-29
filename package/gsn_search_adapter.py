"""Module"""
import os
import subprocess
import time
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv


class GsnSearchAdapter:
    """Class representing a adapter"""

    def __init__(self, host="", raw_host=""):
        if host == "" or raw_host == "":
            load_dotenv()
            self.host = os.getenv("GSN_SEARCH_HOST")
            self.raw_host = os.getenv("GSN_SEARCH_RAW_HOST")
        else:
            self.host = host
            self.raw_host = raw_host

        self.headers = {
            'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            '(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        }
        self.timeout = 10

    def solve_for(self, api_type):
        """ This is a docstring that provides a brief description of my_function."""

        query_maps = {
            'ip': {
                'method_name': [
                    'ip_batch_hourly_count',
                    'ip_hourly_count',
                    'ip_connect_count',
                    'ip_connect_record',
                    'ip_pair_connect_record',
                    'ip_correlated_domain',
                    'dns_reverse_ans',
                    'http_host_by_client',
                    'ip_pair_http_record',
                ],
                'field_name':
                'IPs',
            },
            'http': {
                'method_name': [
                    'http_client',
                    'http_client_record',
                    'http_url_count',
                    'http_record',
                    'http_client_by_url_match',
                ],
                'field_name':
                'URLs',
            },
            'dns': {
                'method_name': [
                    'dns_client',
                    'dns_client_record',
                    'dns_ans',
                ],
                'field_name': 'DNs'
            },
            'dns_a_record': {
                'method_name': [
                    'dns_record',
                ],
                'field_name': [
                    'DN',
                    'IP',
                ]
            },
            'http_record': {
                'method_name': [
                    'http_record',
                ],
                'field_name': [
                    'URLs',
                    'IPs',
                ]
            }
        }

        field_name = None
        for value in query_maps.values():
            if api_type in value['method_name']:
                field_name = value['field_name']

        return field_name

    def solve_for_with_raw_api(self, api_type):
        """ This is a docstring that provides a brief description of my_function."""

        key_maps = {
            'records_by_client_server': [
                'url',
                'method',
                'status_code',
                'timestamp',
                'user_agent',
                'upload(bytes)',
                'download(bytes)',
            ]
        }

        key_names = key_maps.get(api_type)

        return key_names

    def ping(self):
        """ This is a docstring that provides a brief description of my_function."""

        try:
            hostname = urlparse(self.host).hostname
            subprocess.run(['ping', '-c', '1', hostname],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def cancel_task(self, task_id):
        """ This is a docstring that provides a brief description of my_function."""

        try:
            response = requests.get(
                url=f"{self.host}/cancel_task/{task_id}",
                headers=self.headers,
                timeout=self.timeout,
            )
        except requests.exceptions.RequestException as req_err:
            print(req_err)
            return None

        return response.json()

    def get_task(self, task_id):
        """ This is a docstring that provides a brief description of my_function."""

        try:
            response = requests.get(
                url=f"{self.host}/task/{task_id}",
                headers=self.headers,
                timeout=self.timeout,
            )
        except requests.exceptions.RequestException as req_err:
            print(req_err)
            return None

        status = response.json().get('status')

        if status != 'success':
            return None

        return response.json().get('data')

    def get_task_id(self, payload):
        """ This is a docstring that provides a brief description of my_function."""

        try:
            response = requests.post(url=f"{self.host}/task",
                                     headers=self.headers,
                                     json=payload,
                                     timeout=self.timeout)
        except requests.exceptions.RequestException as req_err:
            print(req_err)
            return None

        status = response.json().get('status')

        task_id = None
        if status == 'success':
            task_id = response.json()['data']['task_id']

        return task_id

    def get(self, api_type, request_data, start_date, end_date):
        """ This is a docstring that provides a brief description of my_function."""

        field_name = self.solve_for(api_type)
        payload = {}
        payload['API_type'] = api_type
        payload['start_date'] = start_date
        payload['end_date'] = end_date

        if isinstance(field_name, list):
            for field, data in zip(field_name, request_data.values()):
                payload[field] = data
        else:
            payload[field_name] = request_data

        print(f"payload: {payload}")

        task_id = self.get_task_id(payload)
        print(f"task_id: {task_id}")

        task_result = None

        try:
            while True:
                task_result = self.get_task(task_id)
                task_status = task_result.get('task_status')
                print(f"task_status: {task_status}")
                if task_status == 'finished':
                    task_result = task_result['task_result']['result']
                    break

                if task_status == 'failed':
                    task_result = []
                    break

                time.sleep(5)
        except KeyboardInterrupt:
            print("\nCtrl+C detected. Cleaning up...")
            self.cancel_task(task_id)
            print("Exiting gracefully.")

        return task_result

    def get_with_raw_api(self, api_type, client_address, server_address, date):
        """ This is a docstring that provides a brief description of my_function."""

        try:
            response = requests.get(
                url=(f"{self.raw_host}"
                     f"/http"
                     f"/{date}"
                     f"/{client_address}"
                     f"/{server_address}"
                     f"/{api_type}"),
                headers=self.headers,
                timeout=30,
            )
        except requests.exceptions.RequestException as req_err:
            print(req_err)
            return None

        response = response.json()
        result = response.get('result')

        query_dict = {
            'date': date,
            'client_address': client_address,
            'server_address': server_address,
        }
        keys = self.solve_for_with_raw_api(api_type)
        parsed_result = [query_dict | dict(zip(keys, val))
                         for val in result] if result else []

        return parsed_result


if __name__ == '__main__':
    gs = GsnSearchAdapter()
    records = gs.get_with_raw_api(api_type='records_by_client_server',
                                  client_address='223.200.105.181',
                                  server_address='104.155.217.104',
                                  date='2024-02-01')
    print(records)
