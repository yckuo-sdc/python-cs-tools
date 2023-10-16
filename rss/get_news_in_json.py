"""Module"""
import hashlib
import json
import os
import sys

import feedparser

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'mail'))
from send_mail import SendMail


def load_cs_rss_feeds(filename):
    """Function"""
    path_to_file = os.path.join(os.path.dirname(__file__), filename)
    feeds = []
    if os.path.exists(path_to_file):
        print(f"The file '{path_to_file}' already exists.")
        with open(path_to_file, encoding='utf-8') as f:
            feeds = json.load(f)
    else:
        print(f"The file '{path_to_file}' does not exists.")

    return feeds


def save_cs_rss_feeds(filename, data):
    """Function"""
    path_to_file = os.path.join(os.path.dirname(__file__), filename)
    with open(path_to_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)


def load_previous_state(filename):
    """Function"""
    path_to_file = os.path.join(os.path.dirname(__file__), 'previous_state',
                                filename)

    previous_state = {}
    if os.path.exists(path_to_file):
        print(f"The file '{path_to_file}' already exists.")
        with open(path_to_file, encoding='utf-8') as f:
            previous_state = json.load(f)
    else:
        # Create the file if it doesn't exist
        with open(path_to_file, 'w') as f:
            f.write("{}")
        print(f"The file '{path_to_file}' has been created.")

    return previous_state


def save_previous_state(filename, data):
    """Function"""
    path_to_file = os.path.join(os.path.dirname(__file__), 'previous_state',
                                filename)
    with open(path_to_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)


mail = SendMail()
mail.set_recipient("t910729@gmail.com")
CS_RSS_FEEDS_FILENAME = 'cs_rss_feeds.json'
cs_rss_feeds = load_cs_rss_feeds(CS_RSS_FEEDS_FILENAME)
print(cs_rss_feeds)
for index, feed in enumerate(cs_rss_feeds):
    if 'id' not in feed:
        feed_id = hashlib.sha1(feed['link'].encode()).hexdigest()
        cs_rss_feeds[index]['id'] = feed_id
    else:
        feed_id = feed['id']

    previous_state = load_previous_state(f"{feed_id}.json")
    d = feedparser.parse(feed['link'])

    for entry in d.entries:
        item_title = entry.title
        item_id = entry.id  # Use a unique identifier, like the GUID

        if item_id not in previous_state or previous_state[
                item_id] != item_title:
            print(item_id)
            previous_state[item_id] = item_title

            subject = f"RSS Feed Notifier: {item_title}"
            body = f"published: {entry.published}<br>"
            body += f"link: {entry.link}"

            mail.set_subject(subject)
            mail.set_body(body)
            mail.send()

    save_previous_state(f"{feed_id}.json", previous_state)

save_cs_rss_feeds(CS_RSS_FEEDS_FILENAME, cs_rss_feeds)
