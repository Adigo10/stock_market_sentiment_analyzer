"""
Sentiment Predictor using Fine-tuned Flan-T5 Model
Loads the fine-tuned model and generates sentiment predictions for news articles.
"""

import torch
from transformers import AutoTokenizer, T5ForConditionalGeneration
from pathlib import Path
from typing import Dict, List, Any
import time


class SentimentPredictor:
    """
    Loads the fine-tuned Flan-T5 model and predicts sentiment for financial news.
    """
    
    def __init__(self, model_path: str = None):
        """
        Initialize the sentiment predictor.
        
        Args:
            model_path: Path to the fine-tuned model directory.
                       Defaults to model/Flan_T5_Base in the project root.
        """
        if model_path is None:
            # Default to the model directory in the project
            current_dir = Path(__file__).parent.parent.absolute()
            model_path = current_dir / "model" / "Flan_T5_Base"
        
        self.model_path = Path(model_path)

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model directory not found: {self.model_path}\n"
                "Please ensure the fine-tuned model is available."
            )
        
        print(f"Loading sentiment prediction model from: {self.model_path}")
        load_start = time.time()
        
        # Load tokenizer and model (AutoTokenizer handles SentencePiece automatically)
        self.tokenizer = AutoTokenizer.from_pretrained(str("tssrihari/Flan_T5_Base"))
        self.model = T5ForConditionalGeneration.from_pretrained(str("tssrihari/Flan_T5_Base"))
        
        # Move model to GPU if available
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = self.model.to(self.device)
        self.model.eval()  # Set to evaluation mode
        
        load_time = time.time() - load_start
        print(f"✓ Model loaded successfully in {load_time:.2f}s")
        print(f"  Device: {self.device}")
        print(f"  Model parameters: {self.model.num_parameters():,}")
    
    def predict_single(self, source_text: str, max_length: int = 128, num_beams: int = 4) -> str:
        """
        Predict sentiment for a single news article.
        
        Args:
            source_text: The news article text (headline + summary)
            max_length: Maximum length of generated text
            num_beams: Number of beams for beam search
            
        Returns:
            Generated sentiment prediction string
        """
        # Format input with task prefix
        input_text = f"Analyze the financial sentiment: {source_text}"
        
        # Tokenize
        inputs = self.tokenizer(
            input_text,
            return_tensors="pt",
            max_length=512,
            truncation=True
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Generate prediction
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                num_beams=num_beams,
                early_stopping=True
            )
        
        # Decode the generated text
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        return generated_text
    
    def predict_batch(
        self,
        articles: List[Dict[str, Any]],
        max_length: int = 128,
        num_beams: int = 4,
        batch_size: int = 8
    ) -> List[Dict[str, Any]]:
        """
        Predict sentiment for a batch of news articles.
        
        Args:
            articles: List of article dictionaries with 'headline' and 'summary' fields
            max_length: Maximum length of generated text
            num_beams: Number of beams for beam search
            batch_size: Number of articles to process at once
            
        Returns:
            List of articles with added 'predicted_sentiment' field
        """
        print(f"\n🔮 Running sentiment prediction on {len(articles)} articles...")
        predict_start = time.time()
        
        results = []
        
        for i in range(0, len(articles), batch_size):
            batch = articles[i:i + batch_size]
            batch_inputs = []
            
            # Prepare inputs for batch
            for article in batch:
                # Combine headline and summary as source
                headline = article.get('headline', '') or article.get('title', '')
                summary = article.get('summary', '') or article.get('content', '')
                source = f"{headline}. {summary}"
                
                input_text = f"Analyze the financial sentiment: {source}"
                batch_inputs.append(input_text)
            
            # Tokenize batch
            inputs = self.tokenizer(
                batch_inputs,
                return_tensors="pt",
                max_length=512,
                truncation=True,
                padding=True
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate predictions for batch
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=max_length,
                    num_beams=num_beams,
                    early_stopping=True
                )
            
            # Decode generated texts
            for j, output in enumerate(outputs):
                generated_text = self.tokenizer.decode(output, skip_special_tokens=True)
                
                # Add prediction to article
                article_with_pred = batch[j].copy()
                article_with_pred['predicted_sentiment'] = generated_text
                
                # Extract source for keyphrase analysis
                headline = batch[j].get('headline', '') or batch[j].get('title', '')
                summary = batch[j].get('summary', '') or batch[j].get('content', '')
                article_with_pred['source_text'] = f"{headline}. {summary}"
                
                results.append(article_with_pred)
            
            if (i + batch_size) % 32 == 0 or (i + batch_size) >= len(articles):
                print(f"  Processed {min(i + batch_size, len(articles))}/{len(articles)} articles...")
        
        predict_time = time.time() - predict_start
        print(f"✓ Sentiment prediction completed in {predict_time:.2f}s")
        print(f"  Average: {predict_time/len(articles):.3f}s per article")
        
        return results
    
    def extract_sentiment_label(self, predicted_text: str) -> str:
        """
        Extract sentiment label (Good/Bad/Neutral) from predicted text.
        
        Args:
            predicted_text: The generated sentiment text
            
        Returns:
            Sentiment label: 'Good', 'Bad', or 'Neutral'
        """
        try:
            # Try to extract from structured format
            if 'Sentiment:' in predicted_text:
                sentiment = predicted_text.split('Sentiment:')[1].split('.')[0].strip()
                if sentiment in ['Good', 'Bad', 'Neutral']:
                    return sentiment
            
            # Fallback: search for keywords
            text_lower = predicted_text.lower()
            if 'good' in text_lower or 'positive' in text_lower:
                return 'Good'
            elif 'bad' in text_lower or 'negative' in text_lower:
                return 'Bad'
            else:
                return 'Neutral'
        except:
            return 'Neutral'


if __name__ == "__main__":
    # Test the predictor
    predictor = SentimentPredictor()
    
    # Test single prediction
    test_article = """
    NVIDIA reports record quarterly revenue of $18.12 billion, up 206% year-over-year,
    driven by exceptional demand for AI chips and data center solutions.
    The company's leadership in AI computing continues to strengthen.
    """
    
    print("\n" + "="*80)
    print("TEST PREDICTION")
    print("="*80)
    print(f"Input: {test_article.strip()}")
    
    prediction = predictor.predict_single(test_article)
    print(f"\nPredicted Sentiment: {prediction}")
    print(f"Sentiment Label: {predictor.extract_sentiment_label(prediction)}")
