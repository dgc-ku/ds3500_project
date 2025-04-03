"""
File: funion_class.py

Description: A reusable, extensible framework
for scraping and saving speech transcripts from various sources.
"""

import os
import requests
from collections import defaultdict, Counter
from bs4 import BeautifulSoup
import string
import nltk
from textblob import TextBlob

class Funion:
    def __init__(self, output_folder="speech_transcripts", stopword_file = None):
        """ Constructor """
        self.output_folder = output_folder
        os.makedirs(self.output_folder, exist_ok=True)
        self.data = defaultdict(dict)

        self.stop_words = self.load_stop_words(stopword_file)

        self.results = {
            "word_count": {},
            "word_length": {},
            "sentiment": {},
            "num_words": {}
        }


    def save_transcript(self, text, filename):
        """ Save the scraped text to a file """
        with open(os.path.join(self.output_folder, filename), "w", encoding="utf-8") as f:
            f.write(text)

    def simple_text_parser(self, html):
        """ Parse HTML and extract simple text """
        soup = BeautifulSoup(html, 'html.parser')
        return ' '.join([p.get_text(strip=True) for p in soup.find_all('p')])

    def to_lowercase(self, text):
        """ Convert all text to lowercase """
        return text.lower()

    def remove_punctuation(self, text):
        """ Remove all punctuation from the text, excluding hyphens in compound words """

        return text.translate(str.maketrans('', '', string.punctuation))

    def load_stop_words(self, stopword_file):
        """ Load stop words from a file """

        from nltk.corpus import stopwords
        nltk.download('stopwords')
        stop_words = set(stopwords.words('english'))

        if stopword_file:
            with open(stopword_file, "r", encoding="utf-8") as f:
                stop_words.update(f.read().splitlines())

        return stop_words

    def remove_stop_words(self, text):
        """ Remove stop words from the text """
        words = text.split()
        return ' '.join([word for word in words if word.lower() not in self.stop_words
                         and word.lower() != 'applause'
                         and word.lower() != '–'
                         and word.lower() != '—'])

    def count_words(self, text):
        """ Return word count and frequency count (using Counter) """
        words = text.split()
        wordcount = Counter(words)
        numwords = len(words)
        return {"wordcount": wordcount, "numwords": numwords}

    def calculate_word_length(self, text):
        """ Calculate average word length in the text """
        words = text.split()
        total_chars = sum(len(word) for word in words)
        average_word_length = total_chars / len(words) if words else 0
        return average_word_length

    def analyze_sentiment(self, text):
        """ Analyze sentiment of the text using TextBlob """
        blob = TextBlob(text)
        return blob.sentiment.polarity

    def load_text(self, url, filename, label=None, parser=None):
        """ Fetch and save speech transcript from a URL """

            # Fetch the content from the URL
        r = requests.get(url)
        r.raise_for_status()

        if parser:
             # If there's a custom parser, use it
            transcript = parser(r.content)
        else:

            # Otherwise, use the default HTML parser
            transcript = self.simple_text_parser(r.content)

        transcript = self.to_lowercase(transcript)
        transcript = self.remove_punctuation(transcript)
        transcript = self.remove_stop_words(transcript)

        stats = self.count_words(transcript)
        word_count = stats['wordcount']
        numwords = stats['numwords']

        # Calculate word length and sentiment
        avg_word_length = self.calculate_word_length(transcript)
        sentiment = self.analyze_sentiment(transcript)

        # Store results
        self.data[label or filename] = {
            'word_count': word_count,
            'num_words': numwords,
            'word_length': avg_word_length,
            'sentiment': sentiment
        }

        # Save the transcript and add it to the data dictionary
        self.save_transcript(transcript, filename)
