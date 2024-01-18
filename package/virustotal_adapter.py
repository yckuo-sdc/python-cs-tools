"""Module"""
import os

import virustotal3.core
import virustotal3.errors
from dotenv import load_dotenv


class VirusTotalAdapter:
    """This is a docstring that provides a brief description of MyClass."""
    timeout = 10
    apikey = None

    def __init__(self, apikey=""):

        if apikey == "":
            load_dotenv()
            self.apikey = os.getenv("VT_APIKEY")
        else:
            self.apikey = apikey

    def get_subdomain_and_dns_records(self, domain, dns_record_type):
        """ This is a docstring that provides a brief description of my_function."""

        vt3 = virustotal3.core.Domains(self.apikey)
        relationship = vt3.get_relationship(
            domain=domain,
            relationship="subdomains",
            limit=0,
            timeout=self.timeout,
        )
        if 'error' in relationship:
            return None

        count = relationship['meta']['count']
        relationship = vt3.get_relationship(
            domain=domain,
            relationship="subdomains",
            limit=count,
            timeout=self.timeout,
        )

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

    def get_file_information(self, file_hash):
        """ This is a docstring that provides a brief description of my_function."""

        vt3 = virustotal3.core.Files(self.apikey)
        file_information = vt3.info_file(file_hash, timeout=self.timeout)


        try:
            file_information = vt3.info_file(file_hash, timeout=self.timeout)
        #except virustotal3.errors.VirusTotalApiError as vt3_err:
        #except error as e:
        except Exception:
            pass
            #print(e)
            #print(f"Caught an exception: {vt3_err}")

        return file_information

    def parse_file_information(self, file_information):
        """ This is a docstring that provides a brief description of my_function."""

        parsed_file_information = {}
        try:
            attributes = file_information['data']['attributes']
            parsed_file_information['popular_name'] = attributes['names'][0]
            return parsed_file_information
        except KeyError:
            print(f"KeyError: {KeyError}.")
            return None


if __name__ == '__main__':

    vt = VirusTotalAdapter()
    #response = vt.get_subdomain_and_dns_records(domain="hgzvip.net",
    #                                            dns_record_type=["A"])
    #print(response)
    FILE_HASH = "dc4ca971c4c7df50c5aaee10082c75563151e4cabff67b0890156b4ea90379e0"
    FILE_HASH = "0CDF78CF6BA2B639E0368FD0823C5B6E2C6148D8"
    FILE_HASH = "E56116AE2252D91B4E7F3B2B2F395D3499278E4D"
    result = vt.get_file_information(FILE_HASH)
    #print(result)
    info = vt.parse_file_information(result)
    print(info)
