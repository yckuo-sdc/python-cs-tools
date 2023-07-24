from htmlwebshot import WebShot
import csv

shot = WebShot()

shot.flags = [
    "--quiet",
    "--enable-javascript", 
    "--no-stop-slow-scripts"
    ]

#shot.params = {
#    "--custom-header": "Accept-Encoding gzip",
#    "--minimum-font-size": 50,
#    "--format": "png",
#    "--zoom": 10,
#    "--run-script": "app.js"
#    }

shot.size = (110, 270)
shot.quality = 80  # maximum 100


with open('benign.csv', newline='') as csvfile:

  rows = csv.reader(csvfile)
  next(rows, None)  # skip the headers


  for row in rows:
    for url in row:
      file = 'images/' + url.replace('https://', '').replace(".", "_") + '.jpg'
      print(url)
      shot.create_pic(url,  output=file)




