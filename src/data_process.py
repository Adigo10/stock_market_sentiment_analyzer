import re
import json
import string
from typing import Dict, List, Any
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer

# Download required NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

class DataCleaner:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()
    
    def clean_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean news, forum discussions, and social media posts data using traditional NLP techniques.
        
        Args:
            data: JSON data containing company-related content
            
        Returns:
            Cleaned data dictionary
        """
        cleaned_data = {}
        
        for key, content in data.items():
            if isinstance(content, str):
                cleaned_data[key] = self._clean_text(content)
            elif isinstance(content, list):
                cleaned_data[key] = [self._clean_text(item) if isinstance(item, str) else item for item in content]
            elif isinstance(content, dict):
                cleaned_data[key] = self.clean_data(content)
            else:
                cleaned_data[key] = content
                
        return cleaned_data
    
    def _clean_text(self, text: str) -> str:
        """Clean individual text using traditional NLP techniques."""
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove mentions and hashtags
        text = re.sub(r'@\w+|#\w+', '', text)
        
        # Remove HTML tags
        text = re.sub(r'<.*?>', '', text)
        
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and apply lemmatization
        cleaned_tokens = [
            self.lemmatizer.lemmatize(token) 
            for token in tokens 
            if token not in self.stop_words and len(token) > 2
        ]
        
        return ' '.join(cleaned_tokens)