# Automated-Notice
Automated notice project with selenium.

## Prerequisites
Install selenium and webdriver
- https://pypi.org/project/selenium/ 
## Manually creating files
**Customize env file**
- `cp .env.example .env`
```
NOTICE_HOST=
NOTICE_USERNAME=
NOTICE_PASSWORD=
```
**Get sample excel file**
- `cp .excel.example example.xlsx`

## Publish notices 
**Usage**
```
python3 notice.py -h
usage: notice.py [-h] [--excel EXCEL] [--attach-dir ATTACH_DIR]

options:
  -h, --help            show this help message and exit
  --excel EXCEL         Path to the excel (e.g. ./excel.xlsx)
  --attach-dir ATTACH_DIR
                        Path to the attachment directory (e.g. ./attachments)
```

## Create attachments
**Usage**
```
❯ python3 split_excel_into_attachments.py -h
usage: split_excel_into_attachments.py [-h] [--excel EXCEL] [--attach-dir ATTACH_DIR]

options:
  -h, --help            show this help message and exit
  --excel EXCEL         Path to the excel (e.g. ./excel.xlsx)
  --attach-dir ATTACH_DIR
                        Path to the attachment directory (e.g. ./attachments)
```
