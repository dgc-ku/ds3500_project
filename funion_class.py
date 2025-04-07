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
import numpy as np
import plotly.graph_objects as go

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

    def plot_word_barcharts(self, top_n=10):
        """
        Create matplotlib subplots showing top words per document

        Args:
            funion_instance: Loaded Funion instance
            top_n: Number of top words to show per document
        """
        # get documents
        documents = self.data.items()
        num_docs = len(documents)

        # create grid & figure
        cols = 3
        rows = int(np.ceil(num_docs / cols))

        fig, axes = plt.subplots(rows, cols, figsize=(15, 5 * rows))
        fig.tight_layout(pad=4.0)

        axes = axes.flatten()

        # subplot each document
        for idx, (doc_name, stats) in enumerate(documents):
            ax = axes[idx]
            word_counts = stats['word_count']
            top_words = word_counts.most_common(top_n)

            words = [w[0] for w in top_words]
            counts = [w[1] for w in top_words]

            bars = ax.barh(words, counts, color='#B22222')
            ax.invert_yaxis()  # Highest count at top

            # add word count labels
            for bar in bars:
                width = bar.get_width()
                ax.text(width + 0.10, bar.get_y() + bar.get_height() / 2,
                        f'{int(width)}',
                        ha='left', va='center',
                        fontsize=9)

            # subplot titles and axes
            ax.set_title(doc_name)
            ax.set_xlabel('Word Count')
            ax.grid(True, axis='x', linestyle='--', alpha=0.6)

            # remove empty subplot
        for idx in range(len(documents), len(axes)):
            fig.delaxes(axes[idx])

        plt.suptitle(f'Top {top_n} Words per Document', y=1.02, fontsize=14)
        plt.show()

    def create_word_sankey(self, wordlist=None, k=20):
        """
        create a sankey showing text-to-word relationships
        with n most frequent words per text.
        """

        sources = []
        targets = []
        values = []
        labels = []

        text_word_pairs = []

        # list of docs
        texts = list(self.data.keys())
        labels.extend(texts)

        label_to_index = {label: idx for idx, label in enumerate(labels)}

        # if there's a wordlist
        if wordlist is None:

            # get common word counts
            all_word_counts = Counter()
            for text, stats in self.data.items():
                all_word_counts.update(stats['word_count'])

            # most common words across all docs
            global_top_words = [word for word, count in all_word_counts.most_common(k)]
            labels.extend(global_top_words)
            label_to_index = {label: idx for idx, label in enumerate(labels)}

        else:
            # use top k words across all documents
            all_word_counts = Counter()
            for text, stats in self.data.items():
                all_word_counts.update(stats['word_count'])

            global_top_words = [word for word, count in all_word_counts.most_common(k)]

            # add words to labels
            for word in global_top_words:
                if word not in label_to_index:
                    label_to_index[word] = len(labels)
                    labels.append(word)

            for text, stats in self.data.items():
                text_idx = label_to_index[text]
                word_counts = stats['word_count']

                # get top words in document that are also global top words
                top_words = [word for word, count in word_counts.most_common(k)
                             if word in global_top_words]

                for word in top_words:
                    word_idx = label_to_index[word]
                    sources.append(text_idx)
                    targets.append(word_idx)
                    values.append(word_counts[word])

        # create sankey diagram
        fig = go.Figure(go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=labels,
                color="blue"
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values
            )
        ))

        fig.update_layout(
            title_text=f"Sankey of Top {k} Words in Different National Addresses",
            font_size=12,
            width=800,
            height=600
        )
        return fig

    def show_word_sankey(self, wordlist=None, k=20):
        # display sankey
        fig = self.create_word_sankey(k)
        fig.show()
