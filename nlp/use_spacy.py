"""Module"""
import spacy

# Load the English language model
nlp = spacy.load("en_core_web_sm")

# Sample text
text = "Barack Obama was born in Hawaii. He served as the 44th President of the United States."
text = "More than 17,000 WordPress websites have been compromised in the month of September 2023 with a malware known as Balada Injector, nearly twice the number of detections in August. Of these, 9,000 of the websites are said to have been infiltrated using a recently disclosed security flaw in the tagDiv Composer plugin (CVE-2023-3169, CVSS score: 6.1) that could be exploited by unauthenticated users"
text = "A malicious package hosted on the NuGet package manager for the .NET Framework has been found to deliver a remote access trojan called SeroXen RAT. The package, named Pathoschild.Stardew.Mod.Build.Config and published by a user named Disti, is a typosquat of a legitimate package called Pathoschild.Stardew.ModBuildConfig, software supply chain security firm Phylum said in a report today. While"

# Process the text with spaCy
doc = nlp(text)

colors = {'ORG': 'pink', }
options = {'ents': ['ORG'], 'colors':colors}
spacy.displacy.render(doc, style='ent', options=options)
print(doc.text, '\n')

conditions = ['ORG', 'PERSON', 'PRODUCT']
ents = [(e.text, e.start_char, e.end_char, e.label_) for e in doc.ents if e.label_ in conditions]
print(ents)
