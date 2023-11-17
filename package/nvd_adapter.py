"""Modules"""
import os
import sys
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv
from requests.exceptions import RequestException


class NVDAdapter:
    __host = None
    __apikey = None

    def __init__(self, host="", apikey=""):
        if host == "" or apikey == "":
            load_dotenv()
            self.__host = os.getenv("NVD_HOST")
            self.__apikey = os.getenv("NVD_APIKEY")
        else:
            self.__host = host
            self.__apikey = apikey

    def get_cves(self, params):
        """Method printing python version."""

        query = " ".join(f"{k}:\"{v}\"" for k, v in params.items())
        print(f'Query: {query}')

        url = self.__host + "/cves/2.0"
        headers = {
            'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            "apiKey": self.__apikey
        }

        try:
            response = requests.get(url,
                                    params=params,
                                    headers=headers,
                                    timeout=30)
        except RequestException as req_err:
            print(req_err)
            return None

        # Check if the request was successful (status code 200)
        if response.status_code != 200:
            print(f"Error: {response.status_code}, {response.text}")
            return None

        data = response.json()
        print(f"Results found: {data['totalResults']}")
        return data

    def parse_cve_fields(self, cves):
        """Method printing python version."""
        if cves is None:
            return None

        parsed_cves = []
        for vul in cves['vulnerabilities']:
            cve = vul['cve']
            cpe_matches = cve['configurations'][0]['nodes'][0]['cpeMatch']
            cpes = [m['criteria'] for m in cpe_matches]
            cpe_str = " ".join(cpes)

            parsed_cves.append({
                'id': cve['id'],
                'published_at': cve['published'],
                'last_modified_at': cve['lastModified'],
                'status': cve['vulnStatus'],
                'description': cve['descriptions'][0]['value'],
                'cpe_matches': cpe_str,
            })

        return parsed_cves

    def get_cves_with_cpes(self,
                           pub_start_date="",
                           pub_end_date="",
                           selected_severities=""):
        """Method printing python version."""

        if pub_start_date == "" or pub_end_date == "":
            pub_end_date = datetime.now()
            pub_start_date = pub_end_date - timedelta(days=7)


        if selected_severities == "":
            selected_severities = ['CRITICAL', 'HIGH']

        # Format the datetime object as ISO 8601 string
        pub_start_date_iso8601 = pub_start_date.isoformat()
        pub_end_date_iso8601 = pub_end_date.isoformat()

        cves_with_cpes = []
        for selected_severity in selected_severities:
            params = {
                'pubStartDate': pub_start_date_iso8601,
                'pubEndDate': pub_end_date_iso8601,
                'noRejected': '',
                'virtualMatchString': 'cpe:2.3:*:*:*:*:*:*',
                'cvssV3Severity': selected_severity,
            }
            cves = self.get_cves(params)
            parsed_cves = self.parse_cve_fields(cves)
            for index, value in enumerate(parsed_cves):
                parsed_cves[index]['cvssV3Severity'] = selected_severity.lower(
                )
            cves_with_cpes.extend(parsed_cves)

        return cves_with_cpes

    def get_last_one_week_cves_with_cpes(self):
        """Method printing python version."""

        # Get the current and one week ago datetime
        current_datetime = datetime.now()
        one_week_ago = current_datetime - timedelta(days=8)

        # Format the datetime object as ISO 8601 string
        current_iso8601_datetime = current_datetime.isoformat()
        one_week_ago_iso8601_datetime = one_week_ago.isoformat()

        selected_severities = ['CRITICAL', 'HIGH']

        cves_with_cpes = []
        for selected_severity in selected_severities:
            params = {
                'pubStartDate': one_week_ago_iso8601_datetime,
                'pubEndDate': current_iso8601_datetime,
                'noRejected': '',
                'virtualMatchString': 'cpe:2.3:*:*:*:*:*:*',
                'cvssV3Severity': selected_severity,
            }
            cves = self.get_cves(params)
            parsed_cves = self.parse_cve_fields(cves)
            for index, value in enumerate(parsed_cves):
                parsed_cves[index]['cvssV3Severity'] = selected_severity.lower(
                )
            cves_with_cpes.extend(parsed_cves)

        return cves_with_cpes


if __name__ == '__main__':
    nvd = NVDAdapter()
    one_week_cves = nvd.get_last_one_week_cves_with_cpes()
    print(one_week_cves)
