"""Module"""
import dataclasses
import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from string import Template

import yaml
from dotenv import load_dotenv
from premailer import transform


@dataclasses.dataclass
class EmailServer:
    """Class representing a data class"""
    host: str
    port: str


@dataclasses.dataclass
class EmailCredentials:
    """Class representing a data class"""
    username: str
    password: str


@dataclasses.dataclass
class EmailMessage:
    """Class representing a data class"""
    sender: str
    recipient: str
    subject: str
    body: str
    attachments: list


@dataclasses.dataclass
class EmailContacts:
    """Class representing a data class"""
    group: dict


class SendMail:
    """Class representing a adapter"""

    def __init__(self):
        load_dotenv()
        self.server = EmailServer(host=os.getenv("MAIL_HOST"),
                                  port=os.getenv("MAIL_PORT"))
        self.credentials = EmailCredentials(
            username=os.getenv("MAIL_USERNAME"),
            password=os.getenv("MAIL_APP_PASSWORD"))
        self.message = EmailMessage(sender=os.getenv("MAIL_SENDER"),
                                    recipient=None,
                                    subject=None,
                                    body=None,
                                    attachments=[])
        self.contacts = EmailContacts(group=self.__load_recipients())

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
        """ This is a docstring that provides a brief description of my_function."""
        self.message.recipient = recipient

    def set_predefined_recipient(self, recipient_group):
        """ This is a docstring that provides a brief description of my_function."""
        recipients = self.contacts.group.get(recipient_group, [])
        self.message.recipient = ', '.join(recipients)

    def set_subject(self, subject):
        """ This is a docstring that provides a brief description of my_function."""
        self.message.subject = subject

    def set_body(self, body):
        """ This is a docstring that provides a brief description of my_function."""
        self.message.body = body

    def set_template_body(self, mapping, mapping2=None):
        """ This is a docstring that provides a brief description of my_function."""
        if mapping2:
            template_path = Path(
                os.path.join(os.path.dirname(__file__), 'template',
                             'rwd_ddi_with_download_url.html'))
            template_body = Template(template_path.read_text('utf-8'))
            template_body = template_body.substitute({
                "table": mapping,
                "download_url": mapping2
            })
        else:
            template_path = Path(
                os.path.join(os.path.dirname(__file__), 'template',
                             'rwd_ddi.html'))
            template_body = Template(template_path.read_text('utf-8'))
            template_body = template_body.substitute({"table": mapping})

        # Turns CSS blocks into style attributes with 'premailer'
        self.message.body = transform(template_body,
                                      exclude_pseudoclasses=False)

    def set_template_body_with_rss(self, mapping):
        """ This is a docstring that provides a brief description of my_function."""
        template_path = Path(
            os.path.join(os.path.dirname(__file__), 'template',
                         'rss_news.html'))
        template_body = Template(template_path.read_text('utf-8'))
        template_body = template_body.substitute({"body_content": mapping})

        # Turns CSS blocks into style attributes with 'premailer'
        self.message.body = transform(template_body,
                                      exclude_pseudoclasses=False)

    def add_attachment(self, attachments):
        """ This is a docstring that provides a brief description of my_function."""
        self.message.attachments = attachments

    def send(self):
        """ This is a docstring that provides a brief description of my_function."""
        with smtplib.SMTP(host=self.server.host,
                          port=self.server.port) as smtp:
            try:
                smtp.ehlo()
                smtp.starttls()
                smtp.login(self.credentials.username,
                           self.credentials.password)
                content = MIMEMultipart()
                content["subject"] = self.message.subject
                content["from"] = self.message.sender
                content["to"] = self.message.recipient
                content.attach(MIMEText(self.message.body, "html", "utf-8"))

                if self.message.attachments:
                    print(self.message.attachments)
                    for attachment in self.message.attachments:
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
            except smtplib.SMTPException as smtp_e:
                print("Error message: ", smtp_e)


if __name__ == '__main__':

    mail = SendMail()
    mail.set_predefined_recipient("test")
    mail.set_subject("AA")
    mail.set_body("AA")
    print(vars(mail))
    mail.send()
