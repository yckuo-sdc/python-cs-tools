from package.virustotal import VirusTotal

vt = VirusTotal()
vid = vt.scan_url('https://www.nics.nat.gov.tw')
stats = vt.get_scan_report(vid)
print(stats)
