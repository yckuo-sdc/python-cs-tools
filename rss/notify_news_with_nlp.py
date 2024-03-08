"""Module"""
import os
import re
import sys
from datetime import datetime

import feedparser
import mysql.connector
import spacy
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


def pre_fiter_text(input_string):
    """Functions"""
    text_without_tags = re.sub(r'<.*?>', '', input_string)

    return text_without_tags


def post_filter_tags(input_tags):
    """Functions"""
    unique_tags = list(dict.fromkeys(input_tags))
    tags_without_numbers = list(
        filter(lambda x: not is_numeric(x), unique_tags))

    return tags_without_numbers


def extract_tags(nlp, text):
    """Functions"""
    # Process the text with spaCy
    doc = nlp(text)
    exclude_ent_labels = ['CARDINAL', 'ORDINAL', 'DATE', 'MONEY']

    # Extract tags (named entities)
    extracted_tags = [f"{e.text}" for e in doc.ents]
    #extracted_tags = [f"{e.text}({e.label_})" for e in doc.ents]
    #extracted_tags = [
    #    f"{e.text}({e.label_})" for e in doc.ents
    #    if e.label_ not in exclude_ent_labels
    #]
    filtered_tags = post_filter_tags(extracted_tags)

    return filtered_tags


if __name__ == '__main__':

    # Initialization
    EMPTY_TABLE_BEFORE_INSERTING = False

    load_dotenv()

    # Load the English language model
    en_nlp = spacy.load("en_core_web_sm")
    # Load the Chinese language model
    zh_nlp = spacy.load('zh_core_web_sm')

    mail = SendMail()
    mail.set_predefined_recipient("rss_news")

    # Create a connection to the MySQL server
    connection = mysql.connector.connect(host=os.getenv("DB_HOST"),
                                         user=os.getenv("DB_USERNAME"),
                                         password=os.getenv("DB_PASSWORD"),
                                         database=os.getenv("DB_DATABASE"))

    # Create a cursor object
    cursor = connection.cursor(dictionary=True)

    if EMPTY_TABLE_BEFORE_INSERTING:
        # Truncate the table
        TRUNCATE_QUERY = "TRUNCATE TABLE rss_feed_items"
        cursor.execute(TRUNCATE_QUERY)

    # Fetch data
    SELECT_QUERY = "SELECT * FROM rss_feeds"
    cursor.execute(SELECT_QUERY)
    rss_feeds = cursor.fetchall()
    for row in rss_feeds:
        print(row)

    SELECT_QUERY = "SELECT id FROM rss_feeds WHERE language = 'en'"
    cursor.execute(SELECT_QUERY)
    feed_ids = cursor.fetchall()
    en_feed_ids = [d['id'] for d in feed_ids]

    SELECT_QUERY = "SELECT id FROM rss_feeds WHERE language = 'zh-tw'"
    cursor.execute(SELECT_QUERY)
    feed_ids = cursor.fetchall()
    zh_feed_ids = [d['id'] for d in feed_ids]

    results = []
    for feed in rss_feeds:
        d = feedparser.parse(feed['link'])
        sorted_entries = sorted(d.entries, key=lambda x: x.published)

        # Use placeholders and provide values as parameters
        SELECT_QUERY = "SELECT * FROM rss_feed_items WHERE rss_feed_id = %s"
        feed_data = (feed['id'], )
        cursor.execute(SELECT_QUERY, feed_data)
        feed_items = cursor.fetchall()

        guids = [item['guid'] for item in feed_items]

        new_enties = []
        for entry in sorted_entries:
            if entry.id not in guids:

                fitered_description = pre_fiter_text(entry.description)

                TAG_STR = ""
                if feed['id'] in en_feed_ids:
                    tags_desc = extract_tags(en_nlp, fitered_description)
                    tags_title = extract_tags(en_nlp, entry.title)
                    tags_merge = extract_tags(
                        en_nlp, f"{entry.title}. {fitered_description}")
                    TAG_STR = '|'.join(tags_merge)
                elif feed['id'] in zh_feed_ids:
                    tags_desc = extract_tags(zh_nlp, fitered_description)
                    tags_title = extract_tags(zh_nlp, entry.title)
                    tags_merge = extract_tags(
                        zh_nlp, f"{entry.title}. {fitered_description}")
                    TAG_STR = '|'.join(tags_merge)

                INSERT_QUERY = """
                INSERT INTO rss_feed_items
                (rss_feed_id, guid, title, link, description, tag, published_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                item_data = (feed['id'], entry.id, entry.title, entry.link,
                             fitered_description, TAG_STR,
                             convert_string_to_timestamp(entry.published))

                print(item_data)
                cursor.execute(INSERT_QUERY, item_data)
                connection.commit()
                print(
                    "Data inserted successfully into table using the prepared statement"
                )

                new_enties.append({
                    'data': entry,
                    'tags': tags_merge,
                })

        if not new_enties:
            continue

        today = datetime.now().strftime("%Y-%m-%d")
        subject = f"RSS News with NLP: {feed['title']} on {today}"

        BODY = '<div class="ui relaxed divided list">'
        for entry in new_enties:

            LABEL = ' '.join([
                "<label class='ui label'>" + item + "</label>"
                for item in entry['tags']
            ])

            BODY += '<div class="item">'
            BODY += '<div class="content">'
            BODY += f"<a class='header' href='{entry['data'].link}' target='_blank'>"
            BODY += entry['data'].title
            BODY += '</a>'
            BODY += '<div class="description">'
            BODY += entry['data'].published
            BODY += '<div>' + LABEL + '</div>'

            BODY += '</div>'
            BODY += '</div>'
            BODY += '</div>'

        BODY += '</div>'

        replacement = {"body_content": BODY}
        TEMPLATE_HTML = "rss_news.html"

        mail.set_subject(subject)
        mail.set_template_body_parser(replacement, TEMPLATE_HTML)
        mail.send()

    # Close cursor and connection
    cursor.close()
    connection.close()
