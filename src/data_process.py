import re
import json
import string
from typing import Dict, List, Any, Tuple
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import spacy

# Download required NLTK data
nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)

# Load spaCy model with NER capabilities
nlp = spacy.load("en_core_web_sm")

class FinancialDataCleaner:
    def __init__(self):
        """
        Initialize the financial-aware data cleaner.
            
        """
        # Start with NLTK stopwords
        self.base_stopwords = set(nlp.Defaults.stop_words)
        
        # Financial terms to PRESERVE (never remove these)
        self.financial_preserve = {
            'earnings', 'revenue', 'profit', 'loss', 'debt', 'equity',
            'margin', 'growth', 'decline', 'increase', 'decrease',
            'beat', 'miss', 'exceed', 'surpass', 'guidance', 'forecast',
            'target', 'estimate', 'consensus', 'analyst', 'quarter',
            'annual', 'quarterly', 'stock', 'share', 'dividend',
            'acquisition', 'merger', 'ipo', 'buyback', 'split',
            'approval', 'rejection', 'investigation', 'regulatory',
            'ceo', 'cfo', 'executive', 'management', 'board',
            'up', 'down', 'rise', 'fall', 'surge', 'plunge', 'rally', 'crash'
        }
        
        # Remove financial terms from stopwords
        self.stop_words = self.base_stopwords - self.financial_preserve
        
        self.lemmatizer = WordNetLemmatizer()
        
        # Patterns for protecting/removing financial entities
        self.patterns = {
            'currency': r'[\$€£¥]\s*\d+(?:\.\d+)?\s*[BMK]?|(?:USD|EUR|GBP)\s*\d+(?:\.\d+)?\s*[BMK]?',
            'percentage': r'[+-]?\d+(?:\.\d+)?\s*%|[+-]?\d+(?:\.\d+)?\s+percent',
            'financial_acronyms': r'\b(?:EPS|P/E|PE|ROI|ROE|EBITDA|FCF|YoY|MoM|QoQ|M&A|IPO|CEO|CFO|COO|CTO|FDA|SEC|S&P)\b',
            'quarters': r'\bQ[1-4]\b|\bFY\s*\d{2,4}\b',
            'ratios': r'\d+(?:\.\d+)?\s*[:/x]\s*\d+(?:\.\d+)?'
        }
    
    def protect_financial_patterns(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Protect financial patterns in the text by temporarily replacing them with placeholders.
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (modified text, dictionary of protected placeholders)
        """
        protected = {}
        counter = 0
        
        
        # Protect currency patterns
        for match in re.finditer(self.patterns['currency'], text, re.IGNORECASE):
            placeholder = f"__CURRENCY_{counter}__"
            protected[placeholder] = match.group()
            text = text.replace(match.group(), placeholder, 1)
            counter += 1
    
       
        # Protect percentage patterns
        for match in re.finditer(self.patterns['percentage'], text, re.IGNORECASE):
            placeholder = f"__PERCENT_{counter}__"
            protected[placeholder] = match.group()
            text = text.replace(match.group(), placeholder, 1)
            counter += 1
        
        # Always protect financial acronyms (these are important)
        for match in re.finditer(self.patterns['financial_acronyms'], text, re.IGNORECASE):
            placeholder = f"__ACRONYM_{counter}__"
            protected[placeholder] = match.group()
            text = text.replace(match.group(), placeholder, 1)
            counter += 1
        
        # Protect quarters and fiscal years
        for match in re.finditer(self.patterns['quarters'], text, re.IGNORECASE):
            placeholder = f"__QUARTER_{counter}__"
            protected[placeholder] = match.group()
            text = text.replace(match.group(), placeholder, 1)
            counter += 1
        
        # Protect ratios
        for match in re.finditer(self.patterns['ratios'], text):
            placeholder = f"__RATIO_{counter}__"
            protected[placeholder] = match.group()
            text = text.replace(match.group(), placeholder, 1)
            counter += 1
        
        return text, protected
    
    def _clean_text(self, text: str) -> str:
        """
        Clean individual text using finance-aware NLP techniques.
        
        Args:
            text: Input text
            
        Returns:
            Cleaned text
        """
        # Step 1: Protect or remove financial patterns
        text, protected = self.protect_financial_patterns(text)
        
        # Step 2: Convert to lowercase (but we'll restore protected terms later)
        text = text.lower()
        
        # Step 3: Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Step 4: Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Step 5: Remove mentions and hashtags
        text = re.sub(r'@\w+|#\w+', '', text)
        
        # Step 6: Remove HTML tags
        text = re.sub(r'<.*?>', '', text)
        
        # Step 7: Remove most punctuation but keep some important ones
        # Keep: - (for negative numbers), . (for decimals in protected patterns)
        # Remove everything else
        keep_punct = {'-', '.'}
        remove_punct = ''.join([p for p in string.punctuation if p not in keep_punct])
        text = text.translate(str.maketrans('', '', remove_punct))
        
        # Step 8: Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Step 9: Tokenize
        tokens = word_tokenize(text)
        
        # Step 10: Remove stopwords and apply lemmatization
        # But preserve protected placeholders and financial terms
        cleaned_tokens = []
        for token in tokens:
            # Keep if it's a placeholder
            if token.startswith('__'):
                cleaned_tokens.append(token)
            # Keep if it's a financial term (even if in stopwords)
            elif token.lower() in self.financial_preserve:
                cleaned_tokens.append(self.lemmatizer.lemmatize(token))
            # Keep if it's not a stopword and has reasonable length
            elif token.lower() not in self.stop_words and len(token) > 2:
                cleaned_tokens.append(self.lemmatizer.lemmatize(token))
        
        text = ' '.join(cleaned_tokens)

        # Step 11: Restore protected patterns (with original casing)
        for placeholder, original in protected.items():
            text = text.replace(self._clean_text(placeholder), original.lower())
        return text
    
    def clean_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean news, forum discussions, and social media posts data.
        
        Args:
            data: JSON data containing company-related content
            
        Returns:
            Cleaned data dictionary
        """
        cleaned_data = {}
        for key, content in data.items():
            if isinstance(content, str):
                # Clean the text
                cleaned_text = self._clean_text(content)
                cleaned_data[key] = cleaned_text
                    
            elif isinstance(content, list):
                cleaned_items = []
                for item in content:
                    if isinstance(item, str):
                        cleaned_text = self._clean_text(item)
                        cleaned_items.append(cleaned_text)
                    elif isinstance(item, dict):
                        cleaned_item = self.clean_data(item)
                        cleaned_items.append(cleaned_item)
                    else:
                        cleaned_items.append(item)
                cleaned_data[key] = cleaned_items
            
            elif isinstance(content, dict):
                cleaned_data[key] = self.clean_data(content)
                
            else:
                cleaned_data[key] = content
        
        return cleaned_data
    
    def process_json_file(self, input_file: str,output_file: str) -> Dict[str, Any]:
        """
        Process a JSON file and save cleaned results.
        
        Args:
            input_file: Path to input JSON string
            output_file: Path to output JSON file
            
        Returns:
            Cleaned data dictionary
        """
        data = json.loads(input_file)
        cleaned_data = self.clean_data(data)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
        
        print(f"Data has been cleaned as saved to {output_file}.")
        
        return cleaned_data

# ============= USAGE EXAMPLES =============

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Process JSON file")
    print("="*60)
    
    # Create sample JSON
    sample_data = {
        "articles": [
            {
                "id": 1,
                "title": "Tesla Reports Strong Q3 Results",
                "content": "Tesla reported Q3 earnings of $2.3B, beating analyst estimates by 15%. EPS came in at $0.95 versus expected $0.87. CEO Elon Musk praised the team's execution in the year 2025.",
                "source": "Reuters",
                "date": "2024-10-15"
            },
            {
                "id": 2,
                "title": "Amazon Expands AWS Services",
                "content": "Amazon Web Services announced a $5B investment in new data centers across Europe. The expansion is expected to increase AWS revenue by 20% YoY.",
                "source": "Bloomberg",
                "date": "2024-10-16"
            },
            {
                "id": 3,
                "title": "Apple's Q3 Earnings Surpass Expectations",
                "content": "Apple's Q3 earnings beat expectations by $2.5B, with EPS up 15% YoY. Revenue of $89.5B exceeded analyst consensus. CEO Tim Cook announced a new $10B buyback program. The P/E ratio stands at 28.5x.",
                "source": "TechCrunch",
                "date": "2024-10-17"
            }
        ]
    }
    
    # Save sample
    with open('sample_news.json', 'w') as f:
        json.dump(sample_data, f, indent=2)
    
    # Process with currency/percentage removal
    cleaner = FinancialDataCleaner()
    
    result = cleaner.process_json_file(
        input_file='sample_news.json',
        output_file='cleaned_news.json')
    
    print("\nSample of cleaned data:")
    print(json.dumps(result['articles'][0], indent=2))
