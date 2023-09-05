from mail.send_mail import SendMail
from string import Template
from premailer import transform
from pathlib import Path
from datetime import datetime
from io import StringIO
import pandas as pd
import os
import glob


def find_files_with_name(directory, target_name):
    matches = []
    for file in os.listdir(directory):
        if file.find(target_name) > 0:
            print(os.path.join(directory, file))
            words = file.split('_')  # Split using comma as the delimiter
            matches.append({'path_to_file': os.path.join(directory, file), 'shell_name': words[0], 'net_direction': words[1]})

    return matches

directory = os.path.join(os.path.dirname(__file__), 'data', 'shell_trials')
target_datetime = datetime.now().strftime("%Y_%m_%d")

matches = find_files_with_name(directory, target_datetime)

mail = SendMail()
mail.set_recipient("t910729@gmail.com")

for fmatch in matches:
    #df = pd.read_csv(fmatch['path_to_file'],  usecols=['@timestamp', 'ruleName', 'reason', 'request', 'src', 'dst', 'spt', 'dpt', 'http_success', 'filehash_malicious', 'boturl_malicious'])
    df = pd.read_csv(fmatch['path_to_file'])

    interested_id = []
    for index, row in df.iterrows():
        column_http_success = row['http_success']

        if column_http_success: 
            interested_id.append(index)

    if not interested_id:
        print("No Interested Events")
        continue

    subject = "{} ({}) alert on {}".format(fmatch['shell_name'], fmatch['net_direction'], target_datetime.replace("_", "-"))
    textStream = StringIO()
    df.loc[interested_id].to_csv(textStream,index=False)
    attachments = [
        {'type': 'buffer', 'value': textStream, 'name': fmatch['shell_name'] + '.csv' },
        #{'type': 'path', 'value': fmatch['path_to_file'], 'name': fmatch['shell_name'] + '.csv' },
    ] 

    table = df.loc[interested_id].to_html(justify='left', index=False)
    template = Template(Path(os.path.join(os.path.dirname(__file__), 'mail/template', 'rwd_ddi.html')).read_text())
    body = transform(template.substitute({ "table": table }))

    mail.set_subject(subject)
    mail.set_body(body)
    #mail.add_attachment(attachments)
    mail.send()
