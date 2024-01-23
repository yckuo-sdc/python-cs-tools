#!/usr/bin/python3
import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from string import Template

import yaml
from dotenv import load_dotenv
from premailer import transform


class SendMail:

    def __init__(self, host="", username="", password="", sender=""):
        if host == "":
            load_dotenv()
            self.host = os.getenv("MAIL_HOST")
            self.username = os.getenv("MAIL_USERNAME")
            self.password = os.getenv("MAIL_APP_PASSWORD")
            self.sender = os.getenv("MAIL_SENDER")
        else:
            self.host = host
            self.username = username
            self.password = password
            self.sender = sender

        self.recipient = ""
        self.subject = ""
        self.body = ""
        self.attachments = []
        self.predefined_recipients = self.__load_recipients()

    def __load_recipients(self):
        path_to_yaml = os.path.join(os.path.dirname(__file__),
                                    "recipients.yml")
        try:
            with open(path_to_yaml, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
                return data.get('recipients', {})
        except FileNotFoundError:
            print(f"Error: File '{path_to_yaml}' not found.")
            return {}

    def set_recipient(self, recipient):
        self.recipient = recipient

    def set_predefined_recipient(self, recipient_group):
        recipients = self.predefined_recipients.get(recipient_group, [])
        self.recipient = ', '.join(recipients)

    def set_subject(self, subject):
        self.subject = subject

    def set_body(self, body):
        self.body = body

    def set_template_body(self, mapping, mapping2=None):
        if mapping2:
            template_path = Path(
                os.path.join(os.path.dirname(__file__), 'template',
                             'rwd_ddi_with_download_btn.html'))
            template_body = Template(template_path.read_text('utf-8'))
            template_body = template_body.substitute({
                "table": mapping,
                "url": mapping2
            })
        else:
            template_path = Path(
                os.path.join(os.path.dirname(__file__), 'template',
                             'rwd_ddi.html'))
            template_body = Template(template_path.read_text('utf-8'))
            template_body = template_body.substitute({"table": mapping})

        # Turns CSS blocks into style attributes with 'premailer'
        self.body = transform(template_body, exclude_pseudoclasses=False)

    def set_template_body_with_dict(self, mapping_data):
        template_path = Path(
            os.path.join(os.path.dirname(__file__), 'template',
                         'rwd_ddi_with_download_btn.html'))
        template_body = Template(template_path.read_text('utf-8'))
        template_body = template_body.substitute(mapping_data)
        # Turns CSS blocks into style attributes with 'premailer'
        self.body = transform(template_body, exclude_pseudoclasses=False)

    def add_attachment(self, attachments):
        self.attachments = attachments

    def send(self):
        with smtplib.SMTP(host=self.host, port="587") as smtp:
            try:
                smtp.ehlo()
                smtp.starttls()
                smtp.login(self.username, self.password)
                content = MIMEMultipart()
                content["subject"] = self.subject
                content["from"] = self.sender
                content["to"] = self.recipient
                content.attach(MIMEText(self.body, "html", "utf-8"))

                if self.attachments:
                    print(self.attachments)
                    for attachment in self.attachments:
                        if attachment['type'] == 'buffer':
                            content.attach(
                                MIMEApplication(attachment['value'].getvalue(),
                                                Name=attachment['name']))
                        elif attachment['type'] == 'path':
                            with open(attachment['value'], 'rb') as file:
                                content.attach(
                                    MIMEApplication(file.read(),
                                                    Name=attachment['name']))

                smtp.send_message(content)  # 寄送郵件
                print("Complete!")
            except Exception as e:
                print("Error message: ", e)


if __name__ == '__main__':

    mail = SendMail()
    mail.set_predefined_recipient("ddi_alert")
    #mail.set_recipient("username@gmail.com")
    #mail.set_subject("DDI Alert")
    #mail.set_body(body)
    #mail.send()
