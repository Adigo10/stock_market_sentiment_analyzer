import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tag import pos_tag
import pandas as pd
import numpy as np

# Download required NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)

class DataPreprocessor:
    def __init__(self):
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
    
    def to_lowercase(self, text):
        """Convert text to lowercase"""
        return text.lower()
    
    def remove_html_tags(self, text):
        """Remove HTML tags from text"""
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)
    
    def remove_urls(self, text):
        """Remove URLs from text"""
        return re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    def remove_punctuation(self, text):
        """Remove punctuation from text"""
        return text.translate(str.maketrans('', '', string.punctuation))
    
    def remove_numbers(self, text):
        """Remove numbers from text"""
        return re.sub(r'\d+', '', text)
    
    def remove_extra_whitespace(self, text):
        """Remove extra whitespace and normalize spaces"""
        return ' '.join(text.split())
    
    def tokenize(self, text):
        """Tokenize text into words"""
        return word_tokenize(text)
    
    def remove_stopwords(self, tokens):
        """Remove stopwords from token list"""
        return [token for token in tokens if token.lower() not in self.stop_words]
    
    def stem_tokens(self, tokens):
        """Apply stemming to tokens"""
        return [self.stemmer.stem(token) for token in tokens]
    
    def lemmatize_tokens(self, tokens):
        """Apply lemmatization to tokens"""
        return [self.lemmatizer.lemmatize(token) for token in tokens]
    
    def pos_tag_tokens(self, tokens):
        """Get part-of-speech tags for tokens"""
        return pos_tag(tokens)
    
    def remove_short_words(self, tokens, min_length=2):
        """Remove words shorter than min_length"""
        return [token for token in tokens if len(token) >= min_length]
    
    def preprocess_text(self, text, use_stemming=True, use_lemmatization=False, 
                       remove_stopwords=True, min_word_length=2):
        """Complete preprocessing pipeline"""
        # Basic cleaning
        text = self.to_lowercase(text)
        text = self.remove_html_tags(text)
        text = self.remove_urls(text)
        text = self.remove_punctuation(text)
        text = self.remove_numbers(text)
        text = self.remove_extra_whitespace(text)
        
        # Tokenization
        tokens = self.tokenize(text)
        
        # Remove short words
        tokens = self.remove_short_words(tokens, min_word_length)
        
        # Remove stopwords
        if remove_stopwords:
            tokens = self.remove_stopwords(tokens)
        
        # Stemming or Lemmatization
        if use_stemming:
            tokens = self.stem_tokens(tokens)
        elif use_lemmatization:
            tokens = self.lemmatize_tokens(tokens)
        
        return ' '.join(tokens)
    
    def preprocess_dataframe(self, df, text_column, **kwargs):
        """Preprocess text column in a DataFrame"""
        df[text_column] = df[text_column].apply(
            lambda x: self.preprocess_text(x, **kwargs)
        )
        return df