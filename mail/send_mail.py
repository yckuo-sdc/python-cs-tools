#!/usr/bin/python3
import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from string import Template

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

        self.ddi_alert_recipients = os.getenv("MAIL_DDI_ALERT_RECIPIENTS")
        self.rss_news_recipients = os.getenv("MAIL_RSS_NEWS_RECIPIENTS")
        self.nvd_alert_recipients = os.getenv("MAIL_NVD_ALERT_RECIPIENTS")
        self.recipient = ""
        self.subject = ""
        self.body = ""
        self.attachments = []

    def set_recipient(self, recipient):
        self.recipient = recipient

    def set_ddi_alert_recipients(self):
        self.recipient = self.ddi_alert_recipients

    def set_rss_news_recipients(self):
        self.recipient = self.rss_news_recipients

    def set_nvd_alert_recipients(self):
        self.recipient = self.nvd_alert_recipients

    def set_subject(self, subject):
        self.subject = subject

    def set_body(self, body):
        self.body = body

    def set_template_body(self, mapping):
        template_path = Path(os.path.join(os.path.dirname(__file__), 'template', 'rwd_ddi.html'))
        template_body = Template(template_path.read_text('utf-8'))
        template_body = template_body.substitute({"table": mapping})
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
                #path_to_image = os.path.dirname(__file__) + "/../data/images/koala.jpg"
                #content.attach(MIMEImage(Path(path_to_image).read_bytes(), Name="koala.jpg"))  # 郵件圖片內容
                #path_to_csv_file = os.path.dirname(__file__) + "/../data/shell_trials/chopper_2023_08_22_17_13_58_no_early_stop.csv"
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

    template = Template(
        Path(os.path.dirname(__file__) + "/template/welcome.html").read_text())
    body = template.substitute({"user": "Mike"})

    #textStream = StringIO()
    #df.loc[interested_id].to_csv(textStream,index=False)
    #attachments = [
    #    {'type': 'buffer', 'value': textStream, 'name': 'attch1.csv' },
    #    {'type': 'path', 'value': 'path_to_file', 'name': 'attch2.csv' },
    #]

    mail = SendMail()
    mail.set_recipient("username@gmail.com")
    mail.set_subject("DDI Alert")
    mail.set_body(body)
    #mail.add_attachment(attachments)
    mail.send()
