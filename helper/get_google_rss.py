import json

import feedparser


def parseRSS( rss_url ):
    return feedparser.parse( rss_url )

def getHeadlines(rss_url):
    headlines = []

    feed = parseRSS(rss_url)
    for newsitem in feed['items']:
        headlines.append([ 
            {'title': newsitem['title']},
            {'link': newsitem['link']},
            {'description': newsitem['description']},
            ])

    return headlines

allheadlines = []

newsurls = {
    'googlenews': 'https://news.google.com/news/rss/?hl=en&amp;ned=us&amp;gl=US',
    'Palo Alto Networks News':' https://investors.paloaltonetworks.com/rss/news-releases.xml',
}


for key, url in newsurls.items():
    allheadlines.extend(getHeadlines(url))

jsonStr = json.dumps(allheadlines, indent=1)
print(jsonStr)

#for hl in allheadlines:
#    print(hl)
