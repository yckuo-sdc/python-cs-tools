"""Modules"""
import os
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv
from requests.exceptions import RequestException


class NVDAdapter:
    """Class representing a adapter"""
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
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            '(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            "apiKey":
            self.__apikey
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

    def get_cpe_matches(self, params):
        """Method printing python version."""

        query = " ".join(f"{k}:\"{v}\"" for k, v in params.items())
        print(f'Query: {query}')

        url = self.__host + "/cpematch/2.0"
        headers = {
            'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            '(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            "apiKey":
            self.__apikey
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

        cpe_keys = ['criteria', 'versionStartIncluding', 'versionEndExcluding']
        parsed_cve_fields = []
        for vul in cves['vulnerabilities']:
            cve = vul['cve']
            cpes_with_version = []
            for configuration in cve['configurations']:
                for node in configuration['nodes']:
                    for cpe_match in node['cpeMatch']:
                        matching_values = [
                            cpe_match[key] for key in cpe_keys
                            if key in cpe_match
                        ]
                        cpe_match_value = " | ".join(matching_values)
                        cpes_with_version.append(cpe_match_value)

            cpe_with_version_str = " ".join(cpes_with_version)

            parsed_cve_fields.append({
                'cve_id':
                cve['id'],
                'published_at':
                cve['published'],
                'last_modified_at':
                cve['lastModified'],
                'status':
                cve['vulnStatus'],
                'description':
                cve['descriptions'][0]['value'],  # English language
                'cpe_matches_with_version':
                cpe_with_version_str,
            })

        return parsed_cve_fields

    def parse_cpe_matches_fields(self, cpe_matches):
        """Method printing python version."""
        if cpe_matches is None:
            return None

        parsed_cpe_matches_fields = []
        for match_string in cpe_matches['matchStrings']:
            cpe = match_string['matchString']

            field = {}
            field['criteria'] = cpe.get('criteria')
            field['version_start_including'] = cpe.get('versionStartIncluding')
            field['version_end_excluding'] = cpe.get('versionEndExcluding')
            field['match_strings'] = None

            if 'matches' in cpe:
                field['match_strings'] = [c['cpeName'] for c in cpe['matches']]

            print(field)
            input()
            parsed_cpe_matches_fields.append(field)

        return parsed_cpe_matches_fields

    def get_cpe_matches_in_cves(self, cves):
        """ Method printing python version.

        Args:
            cves(list): cve records.

        Returns:
            dict: cpe matches in cve
        """

        if cves is None:
            return None

        cpe_matches_in_cves = {}
        for cve in cves:
            params = {
                'cveId': cve['cve_id'],
            }

            cpe_matches = self.get_cpe_matches(params)
            parsed_cpe_matches = self.parse_cpe_matches_fields(cpe_matches)
            cpe_matches_in_cves[cve['cve_id']] = parsed_cpe_matches

        return cpe_matches_in_cves

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

            if not parsed_cves:
                continue

            for index, _ in enumerate(parsed_cves):
                parsed_cves[index]['cvssV3Severity'] = selected_severity.lower(
                )
            cves_with_cpes.extend(parsed_cves)

        return cves_with_cpes


if __name__ == '__main__':
    nvd = NVDAdapter()

    #custom_params = {
    #    'cveId': 'CVE-2023-46604',
    #}

    #the_cves = nvd.get_cves(custom_params)
    #the_parsed_cves = nvd.parse_cve_fields(the_cves)
    #print(the_parsed_cves)

    #the_cpe_matches = nvd.get_cpe_matches_in_cves(the_parsed_cves)
    #print(the_cpe_matches)

    custom_params = {
        #'cveId': 'CVE-2023-20198',
        'cveId': 'CVE-2023-6126',
    }

    the_cpe_matches = nvd.get_cpe_matches(custom_params)
    the_parsed_cpe_matches = nvd.parse_cpe_matches_fields(the_cpe_matches)
    print(the_parsed_cpe_matches)
