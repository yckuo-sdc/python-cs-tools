import spacy
import subprocess
from string import punctuation

def extract_keywords(nlp, sequence, special_tags : list = None):
    result = []

    # custom list of part of speech tags we are interested in
    # we are interested in proper nouns, nouns, and adjectives
    # edit this list of POS tags according to your needs. 
    pos_tag = ['PROPN','NOUN','ADJ']

    # create a spacy doc object by calling the nlp object on the input sequence
    doc = nlp(sequence.lower())

    # if special tags are given and exist in the input sequence
    # add them to results by default
    if special_tags:
        tags = [tag.lower() for tag in special_tags]
        for token in doc:
            if token.text in tags:
                result.append(token.text)

    for chunk in doc.noun_chunks:
        final_chunk = ""
        for token in chunk:
            if (token.pos_ in pos_tag):
                final_chunk =  final_chunk + token.text + " "
        if final_chunk:
            result.append(final_chunk.strip())


    for token in doc:
        if (token.text in nlp.Defaults.stop_words or token.text in punctuation):
            continue
        if (token.pos_ in pos_tag):
            result.append(token.text)
    return list(set(result))

if __name__ == "__main__":
    text = "A malicious package hosted on the NuGet package manager for the .NET Framework has been found to deliver a remote access trojan called SeroXen RAT. The package, named Pathoschild.Stardew.Mod.Build.Config and published by a user named Disti, is a typosquat of a legitimate package called Pathoschild.Stardew.ModBuildConfig, software supply chain security firm Phylum said in a report today. While"

    # load the small english language model, 
    nlp = spacy.load("en_core_web_sm")

    print("Loaded language vocabulary")
    print(extract_keywords(nlp, text))
