"""Module"""
import json
import os
import sys

import feedparser

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'mail'))
from send_mail import SendMail


def load_previous_state(filename):
    """Function"""
    path_to_file = os.path.join(os.path.dirname(__file__), 'previous_state', filename)

    previous_state = {}
    if os.path.exists(path_to_file):
        print(f"The file '{path_to_file}' already exists.")
        with open(path_to_file, encoding='utf-8') as f:
            previous_state = json.load(f)
    else:
        # Create the file if it doesn't exist
        with open(path_to_file, 'w') as f:
            f.write("")
        print(f"The file '{path_to_file}' has been created.")

    return previous_state


def save_previous_state(filename, data):
    """Function"""
    path_to_file = os.path.join(os.path.dirname(__file__), 'previous_state', filename)
    with open(path_to_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)


mail = SendMail()
mail.set_recipient("t910729@gmail.com")
filename = 'previous_state.json'
feeds = [
    {
        'link': 'https://www.twcert.org.tw/tw/rss-104-1.xml',
        'filename': 'rss-104-1.json'
    },
    {
        'link': 'https://www.twcert.org.tw/tw/rss-132-1.xml',
        'filename': 'rss-132-1.json'
    },
]

for feed in feeds:
    previous_state = load_previous_state(feed['filename'])
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

    save_previous_state(feed['filename'], previous_state)
