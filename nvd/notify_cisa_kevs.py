"""Module"""
import json
import os
import re
import sys
from datetime import datetime

import mysql.connector
import requests
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

#pylint: disable=wrong-import-position
from mail.send_mail import SendMail

#pylint: enable=wrong-import-position


def is_gmt_format(time_string):
    """Functions"""
    # Define a regular expression pattern to match GMT format
    gmt_pattern = r'^[A-Z][a-z]{2}, \d{1,2} [A-Z][a-z]{2} \d{4} \d{2}:\d{2}:\d{2} GMT$'

    if re.match(gmt_pattern, time_string):
        return True

    return False


def convert_string_to_timestamp(time_string):
    """Functions"""
    if is_gmt_format(time_string):
        date_obj = datetime.strptime(time_string, '%a, %d %b %Y %H:%M:%S GMT')
    else:
        date_obj = datetime.strptime(time_string, '%a, %d %b %Y %H:%M:%S %z')

    timestamp = date_obj.strftime('%Y-%m-%d %H:%M:%S')
    return timestamp


def is_numeric(input_string):
    """Function to check if a string is numeric"""
    return bool(re.match(r'^-?\d+(\.\d+)?$', input_string))


def get_json():
    """Function get json"""
    headers = {
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        '(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    }
    timeout = 10
    try:
        response = requests.get(
            url='https://www.cisa.gov/sites/default/files/feeds/'
            'known_exploited_vulnerabilities.json',
            headers=headers,
            timeout=timeout,
        )
    except requests.exceptions.RequestException as req_err:
        print(req_err)
        return None

    return response.json()


if __name__ == '__main__':

    # Initialization
    EMPTY_TABLE_BEFORE_INSERTING = False

    load_dotenv()

    mail = SendMail()
    mail.set_predefined_recipient("test")

    # Create a connection to the MySQL server
    connection = mysql.connector.connect(host=os.getenv("DB_HOST"),
                                         user=os.getenv("DB_USERNAME"),
                                         password=os.getenv("DB_PASSWORD"),
                                         database=os.getenv("DB_DATABASE"))

    # Create a cursor object
    cursor = connection.cursor(dictionary=True)

    if EMPTY_TABLE_BEFORE_INSERTING:
        # Truncate the table
        TRUNCATE_QUERY = "TRUNCATE TABLE cisa_kevs"
        cursor.execute(TRUNCATE_QUERY)


    result = get_json()
    try:
        total = result['count']
        print(f"Results found: {total}")
    except (KeyError, TypeError):
        sys.exit("No Record")

    SELECT_QUERY = "SELECT * FROM cisa_kevs"
    cursor.execute(SELECT_QUERY)
    cisa_kevs = cursor.fetchall()
    cve_ids = [item['cve_id'] for item in cisa_kevs]

    new_enties = []
    for vul in result['vulnerabilities']:
        if vul['cveID'] not in cve_ids:
            INSERT_QUERY = """
            INSERT INTO cisa_kevs 
            (cve_id, vendor_project, product, vulnerability_name, short_description, required_action, known_ransomware_campaign_use, notes, date_added_at, due_date_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            item_data = (vul['cveID'], vul['vendorProject'], vul['product'],
                         vul['vulnerabilityName'], vul['shortDescription'], vul['requiredAction'],
                         vul['knownRansomwareCampaignUse'], vul['notes'],
                         vul['dateAdded'], vul['dueDate']
            )

            print(item_data)
            cursor.execute(INSERT_QUERY, item_data)
            connection.commit()
            print(
                "Data inserted successfully into table using the prepared statement"
            )

            new_enties.append(vul)

    if not new_enties:
        print("No New Record")

    # Close cursor and connection
    cursor.close()
    connection.close()
