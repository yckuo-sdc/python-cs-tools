#!/usr/bin/python3 
import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import StringIO
from pathlib import Path
from string import Template

import pandas as pd
from dotenv import load_dotenv

grades = {
    "name": ["Mike", "Sherry", "Cindy", "John"],
    "math": [80, 75, 93, 86],
    "chinese": [63, 90, 85, 70]
}

df = pd.DataFrame(grades)
textStream = StringIO()
df.to_csv(textStream,index=False)

load_dotenv()
host = os.getenv("MAIL_HOST")
sender = os.getenv("MAIL_SENDER")
app_password = os.getenv("MAIL_APP_PASSWORD")

recipient = "ussername@gmail.com"

body = "Mike"

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
        content.attach(MIMEApplication(textStream.getvalue(), Name="shell.csv"))

        smtp.send_message(content)  # 寄送郵件
        print("Complete!")
    except Exception as e:
        print("Error message: ", e)
