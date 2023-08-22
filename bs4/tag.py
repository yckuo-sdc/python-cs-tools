from bs4 import BeautifulSoup

html_doc = """
<html><head><title>The Dormouse's story</title></head>
<body>
<p class="title"><b>The Dormouse's story 404</b></p>

<p class="story" style="color:#404444">Once upon a time there were three little sisters; and their names were
<a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
<a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
<a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
and they lived at the bottom of a well.</p>

<p class="story">404</p>
"""

soup = BeautifulSoup(html_doc, 'html.parser')
print(soup.body)

target_text = "elsie"
matched_tags = soup.find_all(lambda tag: len(tag.find_all()) == 0 and target_text in tag.get_text().lower())

for matched_tag in matched_tags:
    print("Matched: {}".format(matched_tag))


#comment_search = soup.find_all(string=re.compile("elsie", re.IGNORECASE))
#print(comment_search)
