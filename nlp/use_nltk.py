import spacy
import nltk
from nltk.corpus import stopwords
from collections import Counter

# Load spaCy and NLTK models
nlp = spacy.load("en_core_web_sm")
nltk.download("stopwords")

# Sample article text
article = """
Natural language processing (NLP) is a subfield of artificial intelligence that focuses on the interaction between computers and humans through natural language.
NLP techniques have many applications, including machine translation, sentiment analysis, and text summarization.
"""
article = """
Natural language processing (NLP) is a subfield of artificial intelligence that focuses on the interaction between computers and humans through natural language.
NLP techniques have many applications, including machine translation, sentiment analysis, and text summarization.
"""

# Preprocess and tokenize the text
def preprocess_text(text):
    text = text.lower()  # Convert to lowercase
    doc = nlp(text)
    tokens = [token.text for token in doc if token.is_alpha and token.text not in stopwords.words('english')]
    return tokens

tokens = preprocess_text(article)

# Calculate word frequencies
keyword_frequencies = Counter(tokens)

# Define the number of top keywords to extract
num_top_keywords = 5

# Extract the top keywords
top_keywords = keyword_frequencies.most_common(num_top_keywords)

# Print the top keywords
for keyword, frequency in top_keywords:
    print(f"{keyword}: {frequency}")
