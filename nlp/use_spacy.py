"""Module"""
import spacy

# Load the English language model
nlp = spacy.load("en_core_web_sm")

# Sample text
text = "Barack Obama was born in Hawaii. He served as the 44th President of the United States."
text = "More than 17,000 WordPress websites have been compromised in the month of September 2023 with a malware known as Balada Injector, nearly twice the number of detections in August. Of these, 9,000 of the websites are said to have been infiltrated using a recently disclosed security flaw in the tagDiv Composer plugin (CVE-2023-3169, CVSS score: 6.1) that could be exploited by unauthenticated users"

# Process the text with spaCy
doc = nlp(text)

# Extract tags (named entities)
tags = [ent.text for ent in doc.ents]

# Print the tags
print(tags)
