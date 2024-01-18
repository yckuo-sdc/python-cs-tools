"""Module"""
import os
import time

import requests
from dotenv import load_dotenv


class VirusTotal:
    """This is a docstring that provides a brief description of MyClass."""

    def __init__(self, host="", apikey=""):
        """
        Constructor for the virustotal class.

        Parameters:
            host (str): VirusTotal Host
            apikey (str): VirusTotal API key
        """
        if host == "" or apikey == "":
            load_dotenv()
            self.host = os.getenv("VT_HOST")
            self.apikey = os.getenv("VT_APIKEY")
        else:
            self.host = host
            self.apikey = apikey

        self.headers = {
            "accept": "application/json",
            "x-apikey": self.apikey,
        }

        self.timeout = 10

    def get_domain_relationships(self, domain, relationship, limit):
        """ This is a docstring that provides a brief description of my_function."""

        params = {'limit': limit}

        try:
            response = requests.get(
                url=f"{self.host}/domains/{domain}/{relationship}",
                headers=self.headers,
                params=params,
                timeout=self.timeout)
        except requests.exceptions.RequestException as req_err:
            print(req_err)
            return False

        if response.status_code != 200:
            return False

        return response.json()

    def get_subdomain_and_dns_records(self, domain, dns_record_type):
        """ This is a docstring that provides a brief description of my_function."""

        relationship = self.get_domain_relationships(domain,
                                                     relationship="subdomains",
                                                     limit=0)

        try:
            count = relationship['meta']['count']
        except (KeyError, TypeError):
            return None

        relationship = self.get_domain_relationships(domain,
                                                     relationship="subdomains",
                                                     limit=count)

        subdomain_and_dns_records = []
        for record in relationship['data']:
            item = {}
            last_dns_records = []
            for last_dns_record in record['attributes']['last_dns_records']:
                if last_dns_record['type'] in dns_record_type:
                    last_dns_records.append(last_dns_record['value'])
            item['domain'] = record['id']
            item['dns_records'] = last_dns_records
            subdomain_and_dns_records.append(item)

        return subdomain_and_dns_records

    def get_ip_report(self, target_ip):
        """ This is a docstring that provides a brief description of my_function."""

        try:
            response = requests.get(
                url=f"{self.host}/ip_addresses/{target_ip}",
                headers=self.headers,
                timeout=self.timeout)
        except requests.exceptions.RequestException as req_err:
            print(req_err)
            return False

        if response.status_code != 200:
            return False

        return response.json()

    def get_file_report(self, filehash):
        """ This is a docstring that provides a brief description of my_function."""

        try:
            response = requests.get(url=f"{self.host}/files/{filehash}",
                                    headers=self.headers,
                                    timeout=self.timeout)
        except requests.exceptions.RequestException as req_err:
            print(req_err)
            return False

        if response.status_code != 200:
            return False

        return response.json()

    def get_url_report(self, url):
        """Retrieve information about a URL."""

        # Send the URL to scan
        try:
            response = requests.post(url=f"{self.host}/urls",
                                     data={"url": url},
                                     headers=self.headers,
                                     timeout=self.timeout)
        except requests.exceptions.RequestException as req_err:
            print(req_err)
            return False

        print(response.status_code)
        if response.status_code != 200:
            return False

        try:
            analysis_id = response.json()['data']['id']
        except (KeyError, TypeError) as access_err:
            print(access_err)
            return False

        print(analysis_id)

        try:
            while True:
                #response = requests.get(url=f"{self.host}/urls/{analysis_id}",
                #                        headers=self.headers,
                #                        timeout=self.timeout)
                response = requests.get(url=f"{self.host}/analyses/{analysis_id}",
                                        headers=self.headers,
                                        timeout=self.timeout)

                if response.status_code != 200:
                    return False

                status = response.json()['data']['attributes']['status']
                print(status)

                if status == 'completed':
                    break

                time.sleep(3)
        except requests.exceptions.RequestException as req_err:
            print(req_err)
            return False

        return response.json()



    def get_malicious_number_by_ips(self, request_ips):
        """ This is a docstring that provides a brief description of my_function."""

        first_seen_index = {}
        is_first_seen = [
            not first_seen_index.setdefault(label, i)
            for i, label in enumerate(request_ips)
        ]
        is_first_seen_id = [first_seen_index[label] for label in request_ips]

        malicious_labels = []
        for id_x, request_ip in enumerate(request_ips):
            if not is_first_seen:
                malicious_labels.append({
                    'vt_malicious_num':
                    malicious_labels[is_first_seen_id[id_x]]
                    ['vt_malicious_num']
                })
                continue

            report = self.get_ip_report(request_ip)

            vt_malicious_num = 0
            try:
                vt_malicious_num = report['data']['attributes'][
                    'last_analysis_stats']['malicious']
            except (KeyError, TypeError):
                pass
            finally:
                malicious_labels.append({'vt_malicious_num': vt_malicious_num})

        return malicious_labels

    def is_malicious_by_filehash(self, filehash):
        """ This is a docstring that provides a brief description of my_function."""

        report = self.get_file_report(filehash)

        try:
            stats = report['data']['attributes']['last_analysis_stats']
        except (KeyError, TypeError):
            return False

        malicious_number = stats['malicious']

        if malicious_number:
            return True

        return False

    def is_malicious_by_url(self, target_url):
        """ This is a docstring that provides a brief description of my_function."""


        report = self.get_url_report(target_url)

        if not report:
            return False

        stats = report['data']['attributes']['stats']
        malicious_number = stats['malicious']
        if malicious_number:
            return True

        return False


if __name__ == '__main__':

    vt = VirusTotal()
    FILE_HASH = "E56116AE2252D91B4E7F3B2B2F395D3499278E4D"
    RESULT = vt.is_malicious_by_filehash(FILE_HASH)
    print(RESULT)

    ip = ['218.161.87.168', '223.200.49.186', '67.225.218.6']
    labels = vt.get_malicious_number_by_ips(ip)
    print(labels)

    result = vt.get_url_report("https://w.google.com.tw")
    print(result)

    result = vt.get_subdomain_and_dns_records(domain="hgzvip.net",
                                              dns_record_type=["A"])
    print(result)
