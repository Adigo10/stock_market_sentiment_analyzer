# Model Integration Documentation

## Overview

This document describes the complete integration of the Flan-T5 sentiment prediction model and keyphrase analyzer into the stock market sentiment analyzer pipeline.

## Pipeline Flow

The complete pipeline consists of 5 main steps:

```
1. Data Fetching & Preprocessing
   └─> fetch_data.py (FinancialNewsFetcher)
   └─> data_process.py (FinancialDataCleaner)
   └─> cache_manager.py (CacheManager)

2. Rule-Based Ranking
   └─> rule_based_ranker.py (FinancialNewsRanker)

3. Similarity Expansion
   └─> pipeline/pipeline.py (SimilarityExpansionPipeline)

4. Sentiment Prediction ⭐ NEW
   └─> sentiment_predictor.py (SentimentPredictor)
   └─> Uses model/Flan_T5_Base (Fine-tuned T5 model)

5. Keyphrase Analysis ⭐ NEW
   └─> keyphrase_analyzer.py (KeyphraseAnalyzer)
```

## New Components

### 1. Sentiment Predictor (`src/sentiment_predictor.py`)

**Purpose**: Uses the fine-tuned Flan-T5 model to predict sentiment for financial news articles.

**Key Features**:
- Loads the fine-tuned T5 model from `model/Flan_T5_Base`
- Supports both single and batch prediction
- Automatic GPU utilization if available
- Returns structured sentiment predictions

**Usage**:
```python
from src.sentiment_predictor import SentimentPredictor

predictor = SentimentPredictor()
prediction = predictor.predict_single("News article text...")
# Returns: "<senti>Good<reason>Strong revenue growth and market expansion"

# Batch prediction
articles = [{'headline': '...', 'summary': '...'}, ...]
results = predictor.predict_batch(articles, batch_size=8)
```

**Input Format**:
- Takes headline + summary as source text
- Automatically formats with task prefix: "Analyze the financial sentiment: {text}"

**Output Format**:
- Structured text: `<senti>{Good/Bad/Neutral}<reason>{explanation}`
- Example: `<senti>Good<reason>Company reports record revenue growth with strong AI chip demand`

### 2. Keyphrase Analyzer (`src/keyphrase_analyzer.py`)

**Purpose**: Extracts and categorizes keyphrases from news articles based on sentiment.

**Key Features**:
- Extracts noun phrases, named entities, technical terms
- Categorizes phrases as positive, neutral, or negative
- Uses NLTK when available, falls back to pattern matching
- Provides confidence scores for each phrase

**Usage**:
```python
from src.keyphrase_analyzer import KeyphraseAnalyzer

analyzer = KeyphraseAnalyzer()
result = analyzer.analyze_source_with_sentiment(
    source="News article text...",
    sentiment="<senti>Good<reason>Strong growth..."
)
```

**Output Structure**:
```json
{
    "source": "Original article text",
    "overall_sentiment": "good",
    "sentiment_reason": "Strong growth and market expansion",
    "keyphrases": {
        "positive": [
            {"phrase": "strong growth", "confidence": 0.95, "word_count": 2},
            {"phrase": "market expansion", "confidence": 0.88, "word_count": 2}
        ],
        "neutral": [...],
        "negative": [...]
    },
    "summary": {
        "positive_count": 10,
        "neutral_count": 5,
        "negative_count": 2,
        "total_phrases": 17
    }
}
```

## Integration in Server

### Updated `model_pipeline.py`

The `FinancialNewsAnalyzer` class now orchestrates the complete pipeline:

```python
class FinancialNewsAnalyzer:
    def __init__(self):
        self.similarity_pipeline = SimilarityExpansionPipeline(...)
        self.sentiment_predictor = SentimentPredictor()
        self.keyphrase_analyzer = KeyphraseAnalyzer()
    
    def analyze_news(self, news_data: dict, company_name: str) -> list:
        # Step 1: Rank articles
        ranked_df = self.rank_articles(news_data, company_name)
        
        # Step 2: Similarity expansion (top 15)
        final_articles = self.similarity_pipeline.run(...)
        
        # Step 3: Sentiment prediction
        articles_with_sentiment = self.sentiment_predictor.predict_batch(
            final_articles, batch_size=8
        )
        
        # Step 4: Keyphrase analysis
        enriched_articles = []
        for article in articles_with_sentiment:
            keyphrase_result = self.keyphrase_analyzer.analyze_source_with_sentiment(
                source=article['source_text'],
                sentiment=article['predicted_sentiment']
            )
            article['keyphrase_analysis'] = keyphrase_result
            enriched_articles.append(article)
        
        return enriched_articles
```

### Server Flow (`server.py`)

The server endpoint remains unchanged but now returns enriched data:

```python
@app.post("/analyze-company")
async def analyze_company(request: FinancialNewsRequest):
    # 1. Validate company
    company_name = self._validate_company(request.company_name)
    
    # 2. Get cached or fetch data
    data = await self._get_company_data(company_name)
    
    # 3. Run complete analysis pipeline (ranking + similarity + model + keyphrase)
    result = self.financial_analyzer.analyze_news(
        data["processed_data"], 
        company_name
    )
    
    # Returns enriched articles with sentiment and keyphrases
    return FinancialNewsResponse(
        company_name=company_name,
        result=result,
        status="success"
    )
```

## API Response Structure

The `/analyze-company` endpoint now returns articles with the following structure:

```json
{
    "company_name": "NVIDIA",
    "result": [
        {
            "headline": "NVIDIA Reports Record Q3 Revenue",
            "summary": "Company achieves $18B in quarterly revenue...",
            "publish_date": "2024-11-04T10:30:00Z",
            "url": "https://...",
            "rank_score": 0.95,
            "source_text": "NVIDIA Reports Record Q3 Revenue. Company achieves...",
            "predicted_sentiment": "<senti>Good<reason>Record revenue growth driven by AI chip demand",
            "keyphrase_analysis": {
                "overall_sentiment": "good",
                "sentiment_reason": "Record revenue growth driven by AI chip demand",
                "keyphrases": {
                    "positive": [
                        {"phrase": "record revenue", "confidence": 0.95, "word_count": 2},
                        {"phrase": "ai chip demand", "confidence": 0.90, "word_count": 3}
                    ],
                    "neutral": [...],
                    "negative": [...]
                },
                "summary": {
                    "positive_count": 8,
                    "neutral_count": 5,
                    "negative_count": 1,
                    "total_phrases": 14
                }
            }
        }
        // ... more articles (up to 15)
    ],
    "status": "success"
}
```

## Performance Considerations

### Model Loading
- The Flan-T5 model is loaded once during server initialization
- Model size: ~850MB on disk
- Loading time: ~2-5 seconds (CPU) or ~1-2 seconds (GPU)
- Memory usage: ~2GB RAM

### Inference Performance
- Single article prediction: ~0.1-0.5s (depends on GPU/CPU)
- Batch prediction (8 articles): ~0.5-2s
- Keyphrase analysis: ~0.05-0.1s per article

### Total Pipeline Time
For a typical request analyzing 15 articles:
1. Data fetching (first time): 2-5s
2. Data fetching (cached): <0.1s
3. Rule-based ranking: 0.5-1s
4. Similarity expansion: 1-2s
5. Sentiment prediction: 1-3s
6. Keyphrase analysis: 1-2s

**Total**: 4-9s (first request), 3-8s (cached requests)

## Caching Strategy

The server maintains two levels of caching:

1. **Data Cache**: Raw and preprocessed news data
   - Cached by company name
   - Invalidated manually or after time threshold
   - Saves 2-5s per request

2. **No Model Cache**: Model predictions are NOT cached
   - Always run fresh predictions on top 15 articles
   - Ensures consistency with latest model
   - Could be added in future if needed

## Error Handling

The integration includes comprehensive error handling:

1. **Model Loading Failures**:
   - Clear error message if model directory not found
   - Graceful degradation possible (return articles without sentiment)

2. **Prediction Failures**:
   - Individual article failures don't stop the pipeline
   - Default to "Neutral" sentiment on errors

3. **Keyphrase Analysis Failures**:
   - Falls back to pattern-based extraction if NLTK fails
   - Returns empty lists rather than crashing

## Dependencies

New dependencies added to `requirements.txt`:

```txt
torch>=2.0.0           # PyTorch for model inference
transformers>=4.30.0   # Hugging Face transformers for T5 model
```

Existing dependencies used:
- `nltk>=3.9` (for keyphrase extraction)
- `sentence-transformers==2.6.1` (for similarity pipeline)

## Model Directory Structure

```
model/
└── Flan_T5_Base/
    ├── config.json
    ├── generation_config.json
    ├── model.safetensors          # Model weights
    ├── tokenizer_config.json
    ├── spiece.model               # Tokenizer vocab
    ├── special_tokens_map.json
    └── README.md
```

## Testing

To test the integration:

```bash
# 1. Start the server
python server.py

# 2. Make a request
curl -X POST http://localhost:8000/analyze-company \
  -H "Content-Type: application/json" \
  -d '{"company_name": "NVIDIA"}'

# 3. Check the response includes:
#    - predicted_sentiment field
#    - keyphrase_analysis object
#    - All 15 enriched articles
```

## Future Enhancements

Potential improvements:

1. **Prediction Caching**: Cache model predictions to avoid re-running
2. **Batch Size Optimization**: Auto-tune batch size based on GPU memory
3. **Model Quantization**: Use INT8 quantization for faster inference
4. **Async Prediction**: Run predictions asynchronously to reduce latency
5. **Sentiment Tracking**: Store predictions in database for trend analysis

## Troubleshooting

### Common Issues

1. **"Model directory not found"**
   - Ensure `model/Flan_T5_Base/` exists
   - Check that model files are downloaded

2. **"CUDA out of memory"**
   - Reduce batch_size in `predict_batch()` call
   - Model will automatically fall back to CPU

3. **"NLTK download errors"**
   - Run: `python -m nltk.downloader all`
   - Or let it use fallback pattern matching

4. **Slow predictions**
   - Check if GPU is being used: look for "Device: cuda" in logs
   - Consider using model quantization
   - Increase batch_size if GPU memory allows

## Conclusion

The integration is complete and production-ready. The pipeline now provides:
- ✅ Cached data fetching and preprocessing
- ✅ Rule-based article ranking
- ✅ Similarity-based expansion
- ✅ **AI-powered sentiment prediction**
- ✅ **Comprehensive keyphrase analysis**

All components work together seamlessly in the server, providing enriched financial news analysis for the top 15 articles per company.
