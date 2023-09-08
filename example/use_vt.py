import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'package'))

from virustotal import VirusTotal

vt = VirusTotal()
vid = vt.scan_url('https://www.nics.nat.gov.tw')
stats = vt.get_scan_report(vid)
print(stats)
