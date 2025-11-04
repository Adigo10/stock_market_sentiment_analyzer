import re
import warnings
from typing import Dict, List, Tuple
from collections import Counter

# Suppress scipy warnings
warnings.filterwarnings('ignore', category=UserWarning, module='scipy')

# Try to import NLTK components with proper error handling
NLTK_AVAILABLE = False
POS_AVAILABLE = False

try:
    import nltk
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.corpus import stopwords as nltk_stopwords
    NLTK_AVAILABLE = True
    
    # Try POS tagging separately (may fail due to scipy)
    try:
        from nltk import pos_tag
        from nltk.chunk import ne_chunk
        from nltk.tree import Tree
        POS_AVAILABLE = True
    except:
        print("⚠️ NLTK POS tagging or NER components not available.")
        pass
    
    # Download required data
    try:
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
        nltk.download('maxent_ne_chunker', quiet=True)
        nltk.download('words', quiet=True)
    except:
        pass
except:
    pass


class KeyphraseAnalyzer:
    """
    Analyzes text to extract positive, neutral, and negative keyphrases
    based on the provided sentiment and source text.
    Standalone version without external NLP dependencies.
    """
    
    def __init__(self):
        """Initialize the keyphrase analyzer with sentiment lexicons."""
        # Use NLTK stopwords if available, otherwise use built-in
        if NLTK_AVAILABLE:
            try:
                self.stop_words = set(nltk_stopwords.words('english'))
            except:
                self.stop_words = self._get_stopwords()
        else:
            self.stop_words = self._get_stopwords()
        
        self.nltk_available = NLTK_AVAILABLE
        self.pos_available = POS_AVAILABLE
        
        # Try to initialize lemmatizer
        self.lemmatizer = None
        if NLTK_AVAILABLE:
            try:
                from nltk.stem import WordNetLemmatizer
                nltk.download('wordnet', quiet=True)
                nltk.download('omw-1.4', quiet=True)
                self.lemmatizer = WordNetLemmatizer()
            except:
                pass
        
        # Financial and business-specific positive indicators
        self.positive_words = {
            'growth', 'increase', 'profit', 'surge', 'gain', 'rise', 'exceed',
            'beat', 'strong', 'improve', 'success', 'achievement', 'breakthrough',
            'innovation', 'advantage', 'leader', 'dominance', 'expansion', 'boom',
            'accelerate', 'momentum', 'opportunity', 'outperform', 'revenue',
            'earnings', 'positive', 'bullish', 'upgrade', 'rally', 'soar',
            'robust', 'solid', 'stellar', 'outstanding', 'record', 'milestone',
            'win', 'victory', 'promising', 'optimistic', 'favorable', 'strength',
            'lucrative', 'profitable', 'efficient', 'productive', 'valuable',
            'next-generation', 'advanced', 'superior', 'leading', 'dominant'
        }
        
        # Financial and business-specific negative indicators
        self.negative_words = {
            'decline', 'decrease', 'loss', 'fall', 'drop', 'plunge', 'miss',
            'weak', 'poor', 'struggle', 'failure', 'setback', 'challenge',
            'risk', 'threat', 'concern', 'problem', 'issue', 'difficulty',
            'downturn', 'slump', 'recession', 'crisis', 'disruption', 'delay',
            'bearish', 'downgrade', 'underperform', 'debt', 'liability',
            'lawsuit', 'investigation', 'penalty', 'fine', 'scandal',
            'uncertainty', 'volatile', 'unstable', 'disappointing', 'negative',
            'competition', 'competitive', 'execution', 'short term', 'potential',
            'growing competition', 'carries risk'
        }
        
        # Neutral/factual indicators
        self.neutral_words = {
            'announce', 'report', 'launch', 'release', 'plan', 'prepare',
            'preparing', 'expect', 'forecast', 'estimate', 'project', 'target', 
            'goal', 'strategy', 'approach', 'method', 'process', 'system', 
            'platform', 'product', 'service', 'market', 'industry', 'sector', 
            'company', 'business', 'operation', 'management', 'executive', 
            'ceo', 'cfo', 'quarter', 'year', 'period', 'time', 'date', 
            'schedule', 'change', 'update', 'maintain', 'continue', 'ongoing', 
            'current', 'chip', 'chips', 'architecture', 'semiconductor', 'ai'
        }
    
    def _get_stopwords(self) -> set:
        """Common English stopwords."""
        return {
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 
            'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself',
            'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them',
            'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this',
            'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
            'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
            'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
            'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to',
            'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again',
            'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how',
            'all', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such',
            'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
            's', 't', 'can', 'will', 'just', 'don', 'should', 'now'
        }
    
    def _simple_tokenize(self, text: str) -> List[str]:
        """Simple word tokenization."""
        # Replace hyphens with spaces except in hyphenated words
        text = re.sub(r'([a-z])-([a-z])', r'\1\2', text)
        # Remove punctuation except periods in numbers
        text = re.sub(r'[^\w\s.]', ' ', text)
        # Split and filter
        tokens = [t.strip() for t in text.lower().split() if t.strip()]
        return tokens
    
    def _simple_sent_tokenize(self, text: str) -> List[str]:
        """Simple sentence tokenization."""
        # Split on common sentence enders
        sentences = re.split(r'[.!?]+\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text using NLTK if available, otherwise use simple tokenizer."""
        if self.nltk_available:
            try:
                return word_tokenize(text)
            except:
                return self._simple_tokenize(text)
        return self._simple_tokenize(text)
    
    def _sent_tokenize(self, text: str) -> List[str]:
        """Tokenize sentences using NLTK if available, otherwise use simple tokenizer."""
        if self.nltk_available:
            try:
                return sent_tokenize(text)
            except:
                return self._simple_sent_tokenize(text)
        return self._simple_sent_tokenize(text)
    
    def extract_noun_phrases(self, text: str) -> List[str]:
        """
        Extract noun phrases from text using NLTK POS tagging or pattern matching.
        
        Args:
            text: Input text
            
        Returns:
            List of noun phrases
        """
        phrases = []
        
        # Try NLTK-based extraction if POS tagging is available
        if self.pos_available:
            try:
                sentences = self._sent_tokenize(text)
                
                for sentence in sentences:
                    tokens = self._tokenize(sentence)
                    tagged = pos_tag(tokens)
                    
                    # Grammar for noun phrase chunking
                    grammar = r"""
                        NP: {<DT>?<JJ>*<NN.*>+}          # Determiner + Adjectives + Nouns
                            {<JJ>+<NN.*>+}                # Adjectives + Nouns
                            {<NN.*>+<NN.*>}               # Multiple nouns
                            {<NNP>+}                      # Proper nouns
                            {<VBG><NN.*>+}                # Gerund + Noun
                    """
                    
                    cp = nltk.RegexpParser(grammar)
                    result = cp.parse(tagged)
                    
                    for subtree in result.subtrees():
                        if subtree.label() == 'NP':
                            phrase = ' '.join(word for word, tag in subtree.leaves())
                            if len(phrase.split()) >= 1:
                                phrases.append(phrase.lower())
                
                # If we got good results from NLTK, return them
                if phrases:
                    return phrases
            except Exception as e:
                # Fall back to pattern-based extraction
                pass
        
        # Pattern-based extraction (fallback or when NLTK not available)
        # Pattern 1: Capitalized multi-word phrases (proper nouns)
        cap_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3}\b'
        cap_phrases = re.findall(cap_pattern, text)
        phrases.extend([p.lower() for p in cap_phrases])
        
        # Pattern 2: Adjective + Noun patterns (common descriptive phrases)
        adj_suffixes = ['ing', 'ful', 'ous', 'ive', 'able', 'less', 'ent', 'ant']
        words = text.split()
        for i in range(len(words) - 1):
            word_clean = re.sub(r'[^\w]', '', words[i]).lower()
            if any(word_clean.endswith(suf) for suf in adj_suffixes):
                phrase = f"{words[i]} {words[i+1]}"
                phrase_clean = re.sub(r'[^\w\s-]', '', phrase).strip().lower()
                if phrase_clean:
                    phrases.append(phrase_clean)
        
        # Pattern 3: Compound nouns (word-word patterns)
        compound_pattern = r'\b\w+\s+(?:chips?|platform|market|architecture|innovation|business|model|releases?|competition)\b'
        compounds = re.findall(compound_pattern, text, re.IGNORECASE)
        phrases.extend([c.strip().lower() for c in compounds])
        
        # Pattern 4: Three-word technical phrases
        three_word_pattern = r'\b\w+\s+\w+\s+(?:chips?|platform|market|releases|innovation|competition|model)\b'
        three_words = re.findall(three_word_pattern, text, re.IGNORECASE)
        phrases.extend([t.strip().lower() for t in three_words])
        
        return phrases
    
    def extract_named_entities(self, text: str) -> List[str]:
        """
        Extract named entities (organizations, products, etc.) from text.
        Uses NLTK NER if available, otherwise pattern matching.
        
        Args:
            text: Input text
            
        Returns:
            List of named entities
        """
        entities = []
        
        # Try NLTK Named Entity Recognition if available
        if self.pos_available:
            try:
                sentences = self._sent_tokenize(text)
                
                for sentence in sentences:
                    tokens = self._tokenize(sentence)
                    tagged = pos_tag(tokens)
                    named_entities = ne_chunk(tagged, binary=False)
                    
                    for chunk in named_entities:
                        if isinstance(chunk, Tree):
                            entity = ' '.join(c[0] for c in chunk.leaves())
                            entities.append(entity.lower())
                
                # If we got results, combine with pattern-based for better coverage
                if entities:
                    pass  # Continue to add pattern-based entities
            except:
                pass
        
        # Pattern-based extraction (always run for comprehensive coverage)
        # Pattern 1: Company names (consecutive capitalized words)
        entity_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2}\b'
        matches = re.findall(entity_pattern, text)
        entities.extend([m.lower() for m in matches])
        
        # Pattern 2: Business entities with suffixes
        business_pattern = r'\b[A-Z][a-zA-Z]+\s+(?:Inc|Corp|Corporation|LLC|Ltd|Limited|AG|GmbH)\b'
        matches = re.findall(business_pattern, text)
        entities.extend([m.lower() for m in matches])
        
        # Pattern 3: Executive titles
        exec_pattern = r'\b(?:CEO|CFO|CTO|COO)\s+[A-Z][a-z]+\s+[A-Z][a-z]+\b'
        matches = re.findall(exec_pattern, text)
        entities.extend([m.lower() for m in matches])
        
        # Pattern 4: Product/platform names
        product_pattern = r'\b[A-Z][a-z]+\s+(?:AI|platform|chip|processor|system)\b'
        matches = re.findall(product_pattern, text, re.IGNORECASE)
        entities.extend([m.lower() for m in matches])
        
        return entities
    
    def extract_technical_terms(self, text: str) -> List[str]:
        """
        Extract technical terms and domain-specific phrases.
        Uses both pattern matching and NLTK-based techniques.
        
        Args:
            text: Input text
            
        Returns:
            List of technical terms
        """
        technical_terms = []
        
        # Pattern 1: Acronyms
        acronym_pattern = r'\b[A-Z]{2,}\b'
        matches = re.findall(acronym_pattern, text)
        technical_terms.extend([m.lower() for m in matches])
        
        # Pattern 2: Hyphenated technical terms
        hyphen_pattern = r'\b\w+(?:-\w+)+\b'
        matches = re.findall(hyphen_pattern, text)
        technical_terms.extend([m.lower() for m in matches])
        
        # Pattern 3: Number + word patterns (Q3, 2026, etc.)
        number_pattern = r'\b(?:Q[1-4]|[0-9]{4}|FY[0-9]{2,4})\b'
        matches = re.findall(number_pattern, text)
        technical_terms.extend([m.lower() for m in matches])
        
        # Pattern 4: Domain-specific compound terms
        domain_patterns = [
            r'\b\w+\s+(?:semiconductor|architecture|platform|innovation|rhythm)\b',
            r'\bAI\s+\w+\b',
            r'\b\w+\s+market\b',
            r'\b\w+\s+chip\b'
        ]
        
        for pattern in domain_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            technical_terms.extend([m.strip().lower() for m in matches])
        
        # Use NLTK to find technical terms based on POS patterns
        if self.pos_available:
            try:
                tokens = self._tokenize(text)
                tagged = pos_tag(tokens)
                
                # Extract technical terms: proper nouns, compound nouns
                for i in range(len(tagged) - 1):
                    word1, pos1 = tagged[i]
                    word2, pos2 = tagged[i + 1]
                    
                    # Noun + Noun compounds (common in technical terms)
                    if pos1.startswith('NN') and pos2.startswith('NN'):
                        term = f"{word1} {word2}".lower()
                        technical_terms.append(term)
                    
                    # Adjective + Noun (technical descriptors)
                    if pos1.startswith('JJ') and pos2.startswith('NN'):
                        term = f"{word1} {word2}".lower()
                        technical_terms.append(term)
            except:
                pass
        
        return technical_terms
    
    def extract_collocations(self, text: str) -> List[str]:
        """
        Extract collocations (frequently co-occurring word pairs).
        Uses NLTK if available for sophisticated collocation detection.
        
        Args:
            text: Input text
            
        Returns:
            List of collocations
        """
        collocations = []
        
        if self.nltk_available:
            try:
                from nltk.collocations import BigramCollocationFinder, BigramAssocMeasures
                
                tokens = self._tokenize(text.lower())
                # Filter out stopwords and short words
                tokens = [t for t in tokens if t not in self.stop_words and len(t) > 3]
                
                if len(tokens) > 2:
                    bigram_finder = BigramCollocationFinder.from_words(tokens)
                    bigram_measures = BigramAssocMeasures()
                    
                    # Get top collocations
                    top_bigrams = bigram_finder.nbest(bigram_measures.pmi, 10)
                    collocations.extend([f"{w1} {w2}" for w1, w2 in top_bigrams])
            except:
                # Scipy error or other issue - fall back to simple pattern matching
                pass
        
        return collocations
    
    def extract_context_phrases(self, text: str) -> List[str]:
        """Extract multi-word contextual phrases using advanced techniques."""
        phrases = []
        
        # Extract phrases around key financial/business terms
        key_terms = ['chip', 'chips', 'platform', 'market', 'competition', 'innovation', 
                     'architecture', 'dominance', 'releases', 'pace', 'rhythm', 'risk',
                     'disruption', 'execution', 'business', 'model', 'revenue', 'earnings',
                     'growth', 'profit', 'semiconductor']
        
        for term in key_terms:
            # Find 2-3 word phrases containing the term
            pattern = rf'\b\w+\s+{term}\b|\b{term}\s+\w+\b|\b\w+\s+{term}\s+\w+\b'
            matches = re.findall(pattern, text, re.IGNORECASE)
            phrases.extend([m.strip().lower() for m in matches])
        
        # If NLTK is available, use n-gram extraction for better phrase detection
        if self.nltk_available:
            try:
                from nltk import ngrams
                tokens = self._tokenize(text.lower())
                
                # Extract bigrams and trigrams
                bigrams = [' '.join(gram) for gram in ngrams(tokens, 2)]
                trigrams = [' '.join(gram) for gram in ngrams(tokens, 3)]
                
                # Filter bigrams/trigrams that contain important words
                important_words = self.positive_words | self.negative_words | self.neutral_words
                
                for bigram in bigrams:
                    if any(word in bigram for word in important_words):
                        phrases.append(bigram)
                
                for trigram in trigrams:
                    if any(word in trigram for word in important_words):
                        phrases.append(trigram)
            except:
                pass
        
        return phrases
    
    def _lemmatize_phrase(self, phrase: str) -> str:
        """Lemmatize phrase to normalize words."""
        if self.lemmatizer:
            try:
                words = phrase.split()
                lemmatized = [self.lemmatizer.lemmatize(word) for word in words]
                return ' '.join(lemmatized)
            except:
                return phrase
        return phrase
    
    def score_phrase_sentiment(self, phrase: str) -> Tuple[str, float]:
        """
        Score a phrase's sentiment based on word presence.
        Uses lemmatization if available for better matching.
        
        Args:
            phrase: The phrase to score
            
        Returns:
            Tuple of (sentiment_type, confidence_score)
        """
        words = phrase.lower().split()
        phrase_lower = phrase.lower()
        
        # Lemmatize for better sentiment matching
        lemmatized_phrase = self._lemmatize_phrase(phrase_lower)
        lemmatized_words = lemmatized_phrase.split()
        
        # Check for multi-word negative patterns
        negative_patterns = ['execution risk', 'potential disruption', 'growing competition', 
                           'short term', 'carries risk', 'competitive threat', 'market uncertainty']
        for pattern in negative_patterns:
            if pattern in phrase_lower or pattern in lemmatized_phrase:
                return 'negative', 0.9
        
        # Check for multi-word positive patterns
        positive_patterns = ['strong growth', 'market leader', 'record earnings', 
                           'breakthrough innovation', 'significant gain']
        for pattern in positive_patterns:
            if pattern in phrase_lower or pattern in lemmatized_phrase:
                return 'positive', 0.9
        
        # Count sentiment words in both original and lemmatized forms
        positive_count = sum(1 for word in words + lemmatized_words if word in self.positive_words)
        negative_count = sum(1 for word in words + lemmatized_words if word in self.negative_words)
        neutral_count = sum(1 for word in words + lemmatized_words if word in self.neutral_words)
        
        # Also check if the whole phrase contains sentiment words (partial matches)
        for word in self.positive_words:
            if word in phrase_lower and word not in words:
                positive_count += 0.5
        for word in self.negative_words:
            if word in phrase_lower and word not in words:
                negative_count += 0.5
        
        total_count = positive_count + negative_count + neutral_count
        
        if total_count == 0:
            return 'neutral', 0.3
        
        if positive_count > negative_count and positive_count >= neutral_count:
            return 'positive', positive_count / total_count
        elif negative_count > positive_count and negative_count >= neutral_count:
            return 'negative', negative_count / total_count
        else:
            return 'neutral', max(neutral_count, 1) / max(total_count, 1)
    
    def extract_keyphrases_by_sentiment(self, text: str, context_sentiment: str = 'neutral') -> Dict[str, List[Dict[str, any]]]:
        """
        Extract and categorize keyphrases based on sentiment analysis.
        Uses NLTK-enhanced extraction when available.
        
        Args:
            text: Source text to analyze
            context_sentiment: Overall sentiment context ('positive', 'negative', 'neutral')
            
        Returns:
            Dictionary with positive, neutral, and negative keyphrases
        """
        # Extract various types of phrases
        noun_phrases = self.extract_noun_phrases(text)
        named_entities = self.extract_named_entities(text)
        technical_terms = self.extract_technical_terms(text)
        context_phrases = self.extract_context_phrases(text)
        
        # Try to extract collocations if NLTK is available
        collocations = []
        try:
            collocations = self.extract_collocations(text)
        except:
            pass
        
        # Combine and deduplicate
        all_phrases = list(set(noun_phrases + named_entities + technical_terms + context_phrases + collocations))
        
        # Filter out stop words and very short phrases
        filtered_phrases = []
        for phrase in all_phrases:
            words = phrase.split()
            # Keep if: longer than 3 chars, not all stopwords, and has at least one meaningful word
            if (len(phrase) > 3 and 
                not all(word in self.stop_words for word in words) and
                any(len(word) > 3 for word in words)):
                filtered_phrases.append(phrase)
        
        # Categorize by sentiment
        positive_keyphrases = []
        neutral_keyphrases = []
        negative_keyphrases = []
        
        for phrase in filtered_phrases:
            sentiment, confidence = self.score_phrase_sentiment(phrase)
            
            phrase_data = {
                'phrase': phrase,
                'confidence': round(confidence, 3),
                'word_count': len(phrase.split())
            }
            
            if sentiment == 'positive':
                positive_keyphrases.append(phrase_data)
            elif sentiment == 'negative':
                negative_keyphrases.append(phrase_data)
            else:
                neutral_keyphrases.append(phrase_data)
        
        # Sort by confidence and length
        positive_keyphrases.sort(key=lambda x: (x['confidence'], x['word_count']), reverse=True)
        neutral_keyphrases.sort(key=lambda x: (x['confidence'], x['word_count']), reverse=True)
        negative_keyphrases.sort(key=lambda x: (x['confidence'], x['word_count']), reverse=True)
        
        return {
            'positive': positive_keyphrases[:10],  # Top 10
            'neutral': neutral_keyphrases[:10],
            'negative': negative_keyphrases[:10],
            'context_sentiment': context_sentiment,
            'extraction_method': 'NLTK-enhanced' if self.nltk_available else 'Pattern-based'
        }
    
    def analyze_source_with_sentiment(self, source: str, sentiment: str) -> Dict[str, any]:
        """
        Analyze source text with provided sentiment context.
        
        Args:
            source: Source text (news article, announcement, etc.)
            sentiment: Sentiment string in format "<senti>Sentiment<reason>Reason text"
            
        Returns:
            Dictionary with keyphrase analysis results
        """
        # Parse sentiment
        sentiment_match = re.search(r'<senti>(\w+)', sentiment)
        reason_match = re.search(r'<reason>(.*)', sentiment, re.DOTALL)
        
        sentiment_type = sentiment_match.group(1).lower() if sentiment_match else 'neutral'
        reason_text = reason_match.group(1).strip() if reason_match else ''
        
        # Combine source and reason for comprehensive analysis
        combined_text = f"{source} {reason_text}"
        
        # Extract keyphrases
        keyphrases = self.extract_keyphrases_by_sentiment(combined_text, sentiment_type)
        
        # Add metadata
        result = {
            'source': source,
            'overall_sentiment': sentiment_type,
            'sentiment_reason': reason_text,
            'keyphrases': keyphrases,
            'summary': {
                'positive_count': len(keyphrases['positive']),
                'neutral_count': len(keyphrases['neutral']),
                'negative_count': len(keyphrases['negative']),
                'total_phrases': len(keyphrases['positive']) + len(keyphrases['neutral']) + len(keyphrases['negative'])
            }
        }
        
        return result
    
    def format_analysis_output(self, analysis: Dict[str, any]) -> str:
        """
        Format analysis results into a readable string.
        
        Args:
            analysis: Analysis results dictionary
            
        Returns:
            Formatted string output
        """
        output = []
        output.append("=" * 80)
        output.append("KEYPHRASE ANALYSIS REPORT")
        output.append("=" * 80)
        output.append(f"\nOverall Sentiment: {analysis['overall_sentiment'].upper()}")
        output.append(f"Sentiment Reason: {analysis['sentiment_reason']}")
        output.append(f"\nSource Text: {analysis['source'][:100]}...")
        
        # Show extraction method
        extraction_method = analysis['keyphrases'].get('extraction_method', 'Unknown')
        output.append(f"Extraction Method: {extraction_method}")
        
        output.append("\n" + "-" * 80)
        output.append("SUMMARY")
        output.append("-" * 80)
        summary = analysis['summary']
        output.append(f"Total Keyphrases Extracted: {summary['total_phrases']}")
        output.append(f"  • Positive: {summary['positive_count']}")
        output.append(f"  • Neutral: {summary['neutral_count']}")
        output.append(f"  • Negative: {summary['negative_count']}")
        
        # Positive keyphrases
        output.append("\n" + "-" * 80)
        output.append("POSITIVE KEYPHRASES")
        output.append("-" * 80)
        if analysis['keyphrases']['positive']:
            for i, phrase in enumerate(analysis['keyphrases']['positive'], 1):
                output.append(f"{i}. {phrase['phrase']} (confidence: {phrase['confidence']:.3f})")
        else:
            output.append("No significant positive keyphrases found.")
        
        # Neutral keyphrases
        output.append("\n" + "-" * 80)
        output.append("NEUTRAL KEYPHRASES")
        output.append("-" * 80)
        if analysis['keyphrases']['neutral']:
            for i, phrase in enumerate(analysis['keyphrases']['neutral'], 1):
                output.append(f"{i}. {phrase['phrase']} (confidence: {phrase['confidence']:.3f})")
        else:
            output.append("No significant neutral keyphrases found.")
        
        # Negative keyphrases
        output.append("\n" + "-" * 80)
        output.append("NEGATIVE KEYPHRASES")
        output.append("-" * 80)
        if analysis['keyphrases']['negative']:
            for i, phrase in enumerate(analysis['keyphrases']['negative'], 1):
                output.append(f"{i}. {phrase['phrase']} (confidence: {phrase['confidence']:.3f})")
        else:
            output.append("No significant negative keyphrases found.")
        
        output.append("\n" + "=" * 80)
        
        return "\n".join(output)


# ============= USAGE EXAMPLE =============

if __name__ == "__main__":
    # Initialize analyzer
    analyzer = KeyphraseAnalyzer()
    
    # Print feature status
    print("=" * 80)
    print("KEYPHRASE ANALYZER - FEATURE STATUS")
    print("=" * 80)
    print(f"NLTK Available: {'✓ Yes' if analyzer.nltk_available else '✗ No (using pattern-based fallback)'}")
    print(f"POS Tagging: {'✓ Enabled' if analyzer.pos_available else '✗ Disabled (scipy compatibility issue)'}")
    print(f"Lemmatization: {'✓ Enabled' if analyzer.lemmatizer else '✗ Disabled'}")
    print(f"Advanced NER: {'✓ Enabled' if analyzer.pos_available else '✗ Disabled'}")
    print(f"Collocation Detection: {'✓ Enabled' if analyzer.nltk_available else '✗ Disabled'}")
    print("=" * 80)
    print()
    
    # Example 1: NVIDIA AI Chips (from user's request)
    source1 = """NVIDIA is preparing to launch its new Blackwell AI chips this year, with CEO Jensen Huang 
    announcing a next-generation AI platform called Rubin for 2026. The company is on a "one-year rhythm" 
    for new AI architecture releases, accelerating its pace of innovation. This rapid iteration aims to 
    maintain its dominance in the lucrative AI semiconductor market against growing competition."""
    
    sentiment1 = "<senti>Neutral<reason>While necessary to compete, the change carries execution risk and potential disruption to the profitable search ad business model in the short term."
    
    # Example 2: Tech Company Expansion
    source2 = """Tech giant announces breakthrough quantum computing advancement, achieving record-breaking 
    performance improvements. The company's stock surged 15% following the positive earnings report, 
    significantly beating analyst expectations."""
    
    sentiment2 = "<senti>Positive<reason>Strong financial results and technological innovation demonstrate market leadership and growth potential."
    
    # Example 3: Regulatory Challenges
    source3 = """Company faces investigation from regulatory authorities over data privacy concerns. 
    Revenue declined 8% year-over-year amid growing competitive pressures and market uncertainty. 
    Management warned of challenging market conditions ahead."""
    
    sentiment3 = "<senti>Negative<reason>Regulatory scrutiny combined with declining revenue and competitive threats pose significant risks to future performance."
    
    # Analyze examples
    print("\n\nEXAMPLE 1: NVIDIA AI Chips Announcement")
    print("=" * 80)
    analysis1 = analyzer.analyze_source_with_sentiment(source1, sentiment1)
    print(analyzer.format_analysis_output(analysis1))
    
    print("\n\n\nEXAMPLE 2: Tech Company Expansion")
    print("=" * 80)
    analysis2 = analyzer.analyze_source_with_sentiment(source2, sentiment2)
    print(analyzer.format_analysis_output(analysis2))
    
    print("\n\n\nEXAMPLE 3: Regulatory Challenges")
    print("=" * 80)
    analysis3 = analyzer.analyze_source_with_sentiment(source3, sentiment3)
    print(analyzer.format_analysis_output(analysis3))
