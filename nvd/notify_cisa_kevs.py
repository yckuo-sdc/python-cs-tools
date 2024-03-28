"""Module"""
import os
import sys
import time

import mysql.connector
import requests
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from mail.send_mail import SendMail
#pylint: disable=wrong-import-position
from package.nvd_adapter import NVDAdapter

#pylint: enable=wrong-import-position


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

    nvd = NVDAdapter()
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

    sorted_entries = sorted(result['vulnerabilities'],
                            key=lambda x: x['dateAdded'])

    SELECT_QUERY = "SELECT * FROM cisa_kevs"
    cursor.execute(SELECT_QUERY)
    cisa_kevs = cursor.fetchall()
    cve_ids = [item['cve_id'] for item in cisa_kevs]

    new_enties = []
    for vul in sorted_entries:
        if vul['cveID'] not in cve_ids:
            cves = nvd.get_cves(params={'cveId': vul['cveID']})
            scores = nvd.parse_cvss_v3_scores(cves)
            CVSS_V3_SCORE = scores[0]['cvss_v3_score'] if scores else None

            INSERT_QUERY = """
            INSERT INTO cisa_kevs 
            (cve_id, vendor_project, product, vulnerability_name, short_description, required_action, known_ransomware_campaign_use, notes, cvss_v3_score, date_added_at, due_date_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            item_data = (vul['cveID'], vul['vendorProject'], vul['product'],
                         vul['vulnerabilityName'], vul['shortDescription'],
                         vul['requiredAction'],
                         vul['knownRansomwareCampaignUse'], vul['notes'],
                         CVSS_V3_SCORE, vul['dateAdded'], vul['dueDate'])

            print(item_data)
            cursor.execute(INSERT_QUERY, item_data)
            connection.commit()
            print(
                "Data inserted successfully into table using the prepared statement"
            )

            new_enties.append(vul | {'cvss_v3_score': CVSS_V3_SCORE})
            time.sleep(10)

    # Close cursor and connection
    cursor.close()
    connection.close()

    if not new_enties:
        sys.exit("No New Record")

    SUBJECT = "VUL Alert: New CISA KEV"

    BODY = '<div class="ui relaxed divided list">'
    for entry in new_enties:
        nvd_link = f"https://nvd.nist.gov/vuln/detail/{entry['cveID']}"
        BODY += '<div class="item">'
        BODY += '<div class="content">'
        BODY += f"<a class='header' href='{nvd_link}' target='_blank'>"
        BODY += entry['cveID']
        BODY += '</a>'
        BODY += '<div class="description">'
        BODY += f"{entry['dateAdded']} to {entry['dueDate']}"

        BODY += '<div class="list">'
        BODY += f"<div class='item'><b>Vendor:</b> {entry['vendorProject']}</div>"
        BODY += f"<div class='item'><b>Product:</b> {entry['product']}</div>"
        BODY += f"<div class='item'><b>CVSSv3:</b> {entry['cvss_v3_score']}</div>"
        BODY += f"<div class='item'><b>Description:</b> {entry['shortDescription']}</div>"
        BODY += f"<div class='item'><b>Action:</b> {entry['requiredAction']}</div>"
        BODY += "<div class='item'><b>Ransomware Campaign Used:</b>"
        BODY += entry['knownRansomwareCampaignUse']
        BODY += "</div>"
        BODY += f"<div class='item'><b>Note:</b> {entry['notes']}</div>"

        BODY += '</div>'
        BODY += '</div>'
        BODY += '</div>'
        BODY += '</div>'

    BODY += '</div>'

    replacement = {"body_content": BODY}
    TEMPLATE_HTML = "rss_news.html"

    mail.set_subject(SUBJECT)
    mail.set_template_body_parser(replacement, TEMPLATE_HTML)
    mail.send()
