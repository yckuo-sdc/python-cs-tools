"""Module"""
import os
import re
import sys
from datetime import datetime

import feedparser
import mysql.connector
import spacy
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'mail'))
from send_mail import SendMail


def is_gmt_format(time_string):
    """functions"""
    # Define a regular expression pattern to match GMT format
    gmt_pattern = r'^[A-Z][a-z]{2}, \d{1,2} [A-Z][a-z]{2} \d{4} \d{2}:\d{2}:\d{2} GMT$'

    # Use re.match to check if the time_string matches the pattern
    if re.match(gmt_pattern, time_string):
        return True

    return False


def convert_string_to_timestamp(time_string):
    """functions"""
    if is_gmt_format(time_string):
        date_obj = datetime.strptime(time_string, '%a, %d %b %Y %H:%M:%S GMT')
    else:
        date_obj = datetime.strptime(time_string, '%a, %d %b %Y %H:%M:%S %z')

    timestamp = date_obj.strftime('%Y-%m-%d %H:%M:%S')
    return timestamp


def is_numeric(input_str):
    """Function to check if a string is numeric"""
    return bool(re.match(r'^-?\d+(\.\d+)?$', input_str))


def filter_tags(tags):
    """functions"""
    unique_tags = list(dict.fromkeys(tags))
    non_numeric_tags= list(filter(lambda x: not is_numeric(x),
                                    unique_tags))

    return non_numeric_tags


def extract_tags(nlp, text):
    """functions"""
    # Process the text with spaCy
    doc = nlp(text)
    # Extract tags (named entities)
    extracted_tags = [ent.text for ent in doc.ents]
    filtered_tags = filter_tags(extracted_tags)

    return filtered_tags


if __name__ == '__main__':

    # Initialization
    ENABLE_NOTIFICATION = True 

    load_dotenv()

    # Load the English language model
    nlp = spacy.load("en_core_web_sm")

    mail = SendMail()
    mail.set_recipient("t910729@gmail.com")

    # Create a connection to the MySQL server
    connection = mysql.connector.connect(host=os.getenv("DB_HOST"),
                                         user=os.getenv("DB_USERNAME"),
                                         password=os.getenv("DB_PASSWORD"),
                                         database=os.getenv("DB_DATABASE"))

    # Create a cursor object
    cursor = connection.cursor(dictionary=True)

    # Fetch data
    SELECT_QUERY = "SELECT * FROM rss_feeds"
    cursor.execute(SELECT_QUERY)
    rss_feeds = cursor.fetchall()
    for row in rss_feeds:
        print(row)

    for feed in rss_feeds:
        d = feedparser.parse(feed['link'])

        # Use placeholders and provide values as parameters
        SELECT_QUERY = "SELECT * FROM rss_feed_items WHERE rss_feed_id = %s"
        feed_data = (feed['id'], )
        cursor.execute(SELECT_QUERY, feed_data)
        feed_items = cursor.fetchall()

        guids = [item['guid'] for item in feed_items]

        for entry in d.entries:
            if entry.id not in guids:

                TAG_STR = ""
                if feed['id'] in [3, 4, 5]:
                    tags = extract_tags(nlp, entry.description)
                    TAG_STR = '|'.join(tags)

                print(entry.id)
                INSERT_QUERY = """
                INSERT INTO rss_feed_items 
                (rss_feed_id, guid, title, link, description, tag, published_at) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                item_data = (feed['id'], entry.id, entry.title, entry.link,
                             entry.description, TAG_STR,
                             convert_string_to_timestamp(entry.published))
                print(item_data)
                cursor.execute(INSERT_QUERY, item_data)
                connection.commit()
                print(
                    "Data inserted successfully into table using the prepared statement"
                )

                if ENABLE_NOTIFICATION:
                    # notify new itmes in channels
                    subject = f"RSS Feed Notifier: {entry.title}"
                    body = f"published: {entry.published}<br>"
                    body += f"link: {entry.link}"
                    mail.set_subject(subject)
                    mail.set_body(body)
                    mail.send()

    # Close cursor and connection
    cursor.close()
    connection.close()
