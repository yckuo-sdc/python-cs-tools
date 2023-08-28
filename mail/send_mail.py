#!/usr/bin/python3 
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from pathlib import Path
from string import Template
from dotenv import load_dotenv
import smtplib
import os

class SendMail: 

    def __init__(self,  host="", username="", password="", sender=""): 
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

    def set_recipient(self, recipient):
        self.recipient = recipient

    def set_subject(self, subject):
        self.subject = subject

    def set_body(self, body):
        self.body = body

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
                #with open(path_to_csv_file,'rb') as file:
                #    content.attach(MIMEApplication(file.read(), Name="shell.csv"))
    
                smtp.send_message(content)  # 寄送郵件
                print("Complete!")
            except Exception as e:
                print("Error message: ", e)


if __name__ == '__main__':

    template = Template(Path(os.path.dirname(__file__) + "/template/welcome.html").read_text())
    body = template.substitute({ "user": "Mike" })

    mail = SendMail()
    mail.set_recipient("t910729@gmail.com")
    mail.set_subject("DDI Alert")
    mail.set_body(body)
    mail.send()
