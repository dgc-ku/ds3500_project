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
import matplotlib.pyplot as plt
import seaborn as sns

class Funion:
    def __init__(self, output_folder="speech_transcripts", stopword_file=None):
        """ Constructor """
        self.output_folder = output_folder
        os.makedirs(self.output_folder, exist_ok=True)
        self.data = defaultdict(dict)
        self.stop_words = self.load_stop_words(stopword_file)

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
        r = requests.get(url)
        r.raise_for_status()

        if parser:
            transcript = parser(r.content)
        else:
            transcript = self.simple_text_parser(r.content)

        transcript = self.to_lowercase(transcript)
        transcript = self.remove_punctuation(transcript)
        transcript = self.remove_stop_words(transcript)

        stats = self.count_words(transcript)
        word_count = stats['wordcount']
        numwords = stats['numwords']

        avg_word_length = self.calculate_word_length(transcript)
        sentiment = self.analyze_sentiment(transcript)

        self.data[label or filename] = {
            'word_count': word_count,
            'num_words': numwords,
            'word_length': avg_word_length,
            'sentiment': sentiment
        }

        self.save_transcript(transcript, filename)

    def plot_summary(self):
        """Create a scatter plot of word count vs sentiment, with 
        point size = avg word length"""
        countries = []
        word_counts = []
        sentiments = []
        avg_word_lengths = []

        for country, stats in self.data.items():
            countries.append(country)
            word_counts.append(stats['num_words'])
            sentiments.append(stats['sentiment'])
            avg_word_lengths.append(stats['word_length'])

        # Set up the plot
        plt.figure(figsize=(12, 8))
        scatter = plt.scatter(
            word_counts,
            sentiments,
            s=[length * 80 for length in avg_word_lengths],  # Scale for visibility
            c=sns.color_palette("hls", len(countries)),
            alpha=0.7
        )

        # Annotate each point
        for i, label in enumerate(countries):
            plt.text(word_counts[i], sentiments[i] + 0.01, label, fontsize=9, 
                     ha='center')

        # Add styling
        plt.axhline(0, color='gray', linestyle='--', linewidth=0.8)
        plt.title("Comparative Sentiment Analysis of Speeches", fontsize=16)
        plt.xlabel("Word Count", fontsize=12)
        plt.ylabel("Sentiment Polarity", fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        plt.show()
