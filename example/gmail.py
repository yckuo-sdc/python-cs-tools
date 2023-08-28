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

load_dotenv()
host = os.getenv("MAIL_HOST")
sender = os.getenv("MAIL_SENDER")
app_password = os.getenv("MAIL_APP_PASSWORD")

recipient = "t910729@gmail.com"

template = Template(Path(os.path.dirname(__file__) + "/template/welcome.html").read_text())
body = template.substitute({ "user": "Mike" })

with smtplib.SMTP(host=host, port="587") as smtp:  # 設定SMTP伺服器
    try:
        smtp.ehlo()  # 驗證SMTP伺服器
        smtp.starttls()  # 建立加密傳輸
        smtp.login(sender, app_password)  # 登入寄件者gmail
        content = MIMEMultipart()  # 建立MIMEMultipart物件
        content["subject"] = "DDI Alert"  # 郵件標題
        content["from"] = sender  # 寄件者
        content["to"] = recipient  # 收件者
        #content.attach(MIMEText("DDI Alert Test", "plain", "utf-8"))  # 郵件純文字內容
        content.attach(MIMEText(body, "html", "utf-8"))  # HTML郵件內容
        content.attach(MIMEImage(Path(os.path.dirname(__file__) + "/../data/images/koala.jpg").read_bytes(), Name="koala.jpg"))  # 郵件圖片內容
        path_to_csv_file = os.path.dirname(__file__) + "/../data/shell_trials/chopper_2023_08_22_17_13_58_no_early_stop.csv" 
        with open(path_to_csv_file,'rb') as file:
            content.attach(MIMEApplication(file.read(), Name="shell.csv"))

        smtp.send_message(content)  # 寄送郵件
        print("Complete!")
    except Exception as e:
        print("Error message: ", e)
