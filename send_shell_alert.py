from mail.send_mail import SendMail
from string import Template
from premailer import transform
from pathlib import Path
from datetime import datetime
import pandas as pd
import os
import glob


def find_files_with_name(directory, target_name):
    matches = []
    for file in os.listdir(directory):
        if file.find(target_name) > 0:
            print(os.path.join(directory, file))
            words = file.split('_')  # Split using comma as the delimiter
            matches.append({'path_to_file': os.path.join(directory, file), 'shell_name': words[0]})

    return matches

directory = os.path.dirname(__file__) + "/data/shell_trials"
target_datetime = datetime.now().strftime("%Y_%m_%d")

matches = find_files_with_name(directory, target_datetime)

mail = SendMail()
mail.set_recipient("t910729@gmail.com")

for fmatch in matches:
    df = pd.read_csv(fmatch['path_to_file'],  usecols=['@timestamp', 'ruleName', 'reason', 'request', 'src', 'dst', 'spt', 'dpt', 'is_gov', 'network_reachable', 'http_success', 'filehash_malicious', 'boturl_malicious'])

    interested_id = []
    for index, row in df.iterrows():
        column_http_success = row['http_success']

        if column_http_success: 
            interested_id.append(index)

    if not interested_id:
        print("No Interested Events")
        continue

    table = df.loc[interested_id].to_html(justify='left')
    template = Template(Path(os.path.dirname(__file__) + "/mail/template/ddi.html").read_text())
    body = transform(template.substitute({ "table": table }))

    mail.set_subject("{} alert on {}".format(fmatch['shell_name'], target_datetime.replace("_", "-")))
    mail.set_body(body)
    mail.send()
