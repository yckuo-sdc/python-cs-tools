from package.virustotal import VirusTotal
import os

vt = VirusTotal()
vid = vt.scan_url('https://www.nics.nat.gov.tw')
stats = vt.get_scan_report(vid)
print(stats)

print('__file__:    ', __file__)

print('dirname:     ', os.path.dirname(__file__))

