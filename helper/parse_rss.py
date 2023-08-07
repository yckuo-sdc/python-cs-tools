import feedparser
d = feedparser.parse('https://investors.paloaltonetworks.com/rss/news-releases.xml')
print(d)
