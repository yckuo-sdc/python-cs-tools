import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'package'))

from virustotal import VirusTotal

vt = VirusTotal()
