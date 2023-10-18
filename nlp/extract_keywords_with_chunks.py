import spacy 

# Load the Spacy model and create a new document 
nlp = spacy.load("en_core_web_sm") 
#doc = nlp("This is a sample text for keyword extraction.") 
doc = nlp('The Computer Emergency Response Team of Ukraine (CERT-UA) has revealed that threat actors "interfered" with at least 11 telecommunication service providers in the country between May and September 2023. The agency is tracking the activity under the name UAC-0165, stating the intrusions led to service interruptions for customers. The starting point of the attacks is a reconnaissance phase in')

# Use the noun_chunks property of the document to identify the noun phrases in the text 
noun_phrases = [chunk.text for chunk in doc.noun_chunks] 
print(noun_phrases)

# Use term frequency-inverse document frequency (TF-IDF) analysis to rank the noun phrases 
from sklearn.feature_extraction.text import TfidfVectorizer 
vectorizer = TfidfVectorizer() 
tfidf = vectorizer.fit_transform([doc.text]) 

# Get the top 3 most important noun phrases 
top_phrases = sorted(vectorizer.vocabulary_, key=lambda x: tfidf[0, vectorizer.vocabulary_[x]], reverse=True)[:3] 

# Print the top 3 keywords 
print(top_phrases)
