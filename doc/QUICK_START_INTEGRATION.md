# Quick Start Guide - Model Integration

## Overview

The sentiment prediction model (Flan-T5) and keyphrase analyzer have been successfully integrated into the server pipeline. This guide will help you get started quickly.

## What Changed?

### Before Integration
```
Server Flow:
1. Fetch & Preprocess Data → Cache
2. Rule-Based Ranking
3. Similarity Expansion → Top 15 Articles
4. Return JSON Response
```

### After Integration
```
Server Flow:
1. Fetch & Preprocess Data → Cache
2. Rule-Based Ranking
3. Similarity Expansion → Top 15 Articles
4. ⭐ Sentiment Prediction (Flan-T5 Model) → Add predicted_sentiment
5. ⭐ Keyphrase Analysis → Add keyphrase_analysis
6. Return Enriched JSON Response
```

## Quick Start

### 1. Install New Dependencies

```bash
pip install torch>=2.0.0 transformers>=4.30.0
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

### 2. Verify Model Files

Ensure the fine-tuned model is available at:
```
model/Flan_T5_Base/
  ├── config.json
  ├── model.safetensors
  ├── tokenizer_config.json
  └── ... (other files)
```

### 3. Start the Server

```bash
python server.py
```

You should see:
```
Initializing Sentiment Predictor...
✓ Model loaded successfully in 2.34s
  Device: cuda  # or 'cpu'
  Model parameters: 247,577,856

Initializing Keyphrase Analyzer...
```

### 4. Test the API

```bash
curl -X POST http://localhost:8000/analyze-company \
  -H "Content-Type: application/json" \
  -d '{"company_name": "NVIDIA"}'
```

### 5. Verify the Response

The response should now include two new fields for each article:

```json
{
  "company_name": "NVIDIA",
  "result": [
    {
      "headline": "...",
      "summary": "...",
      "rank_score": 0.95,
      
      // NEW: Sentiment prediction from Flan-T5
      "predicted_sentiment": "<senti>Good<reason>Strong revenue growth...",
      "source_text": "...",
      
      // NEW: Keyphrase analysis
      "keyphrase_analysis": {
        "overall_sentiment": "good",
        "sentiment_reason": "Strong revenue growth...",
        "keyphrases": {
          "positive": [
            {"phrase": "strong growth", "confidence": 0.95, "word_count": 2}
          ],
          "neutral": [...],
          "negative": [...]
        },
        "summary": {
          "positive_count": 8,
          "neutral_count": 5,
          "negative_count": 2,
          "total_phrases": 15
        }
      }
    }
    // ... up to 15 articles
  ],
  "status": "success"
}
```

## Understanding the Output

### 1. `predicted_sentiment`

Format: `<senti>{Label}<reason>{Explanation}`

- **Label**: `Good`, `Bad`, or `Neutral`
- **Explanation**: AI-generated reason for the sentiment

Example:
```
<senti>Good<reason>Company reports record quarterly earnings with 
strong AI chip demand driving revenue growth and market expansion.
```

### 2. `keyphrase_analysis`

Extracted and categorized keyphrases:

```json
{
  "overall_sentiment": "good",           // Parsed sentiment label
  "sentiment_reason": "Record earnings...", // Parsed reason
  "keyphrases": {
    "positive": [                        // Bullish phrases
      {"phrase": "record earnings", "confidence": 0.95, "word_count": 2},
      {"phrase": "strong demand", "confidence": 0.90, "word_count": 2}
    ],
    "neutral": [                         // Factual phrases
      {"phrase": "quarterly report", "confidence": 0.85, "word_count": 2}
    ],
    "negative": [                        // Bearish phrases
      {"phrase": "competitive pressure", "confidence": 0.88, "word_count": 2}
    ]
  },
  "summary": {
    "positive_count": 8,
    "neutral_count": 5,
    "negative_count": 2,
    "total_phrases": 15
  }
}
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         SERVER.PY                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              APIHandler                               │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │  analyze_company(company_name)                  │  │  │
│  │  │    1. Validate company                          │  │  │
│  │  │    2. Get cached/fetch data                     │  │  │
│  │  │    3. Call financial_analyzer.analyze_news()    │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   MODEL_PIPELINE.PY                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         FinancialNewsAnalyzer                         │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │  analyze_news(news_data, company_name)         │  │  │
│  │  │    Step 1: Rank articles                       │  │  │
│  │  │    Step 2: Similarity expansion                │  │  │
│  │  │    Step 3: ⭐ Sentiment prediction             │  │  │
│  │  │    Step 4: ⭐ Keyphrase analysis               │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
           │                              │
           ▼                              ▼
┌──────────────────────┐    ┌──────────────────────────────┐
│ SENTIMENT_PREDICTOR  │    │   KEYPHRASE_ANALYZER         │
│  ┌────────────────┐  │    │  ┌────────────────────────┐  │
│  │ Flan-T5 Model  │  │    │  │ Extract noun phrases   │  │
│  │ (Fine-tuned)   │  │    │  │ Categorize sentiment   │  │
│  │                │  │    │  │ Score confidence       │  │
│  │ Predicts:      │  │    │  └────────────────────────┘  │
│  │ Good/Bad/      │  │    │                              │
│  │ Neutral +      │  │    │  Uses NLTK + pattern         │
│  │ Reason         │  │    │  matching                    │
│  └────────────────┘  │    └──────────────────────────────┘
└──────────────────────┘
```

## Performance Tips

### 1. GPU Acceleration (Recommended)

If you have a CUDA-capable GPU:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

The model will automatically use GPU if available, significantly speeding up predictions:
- CPU: ~0.5s per article
- GPU: ~0.1s per article

### 2. Batch Size Tuning

The default batch size is 8. Adjust in `model_pipeline.py`:

```python
# For faster processing with more GPU memory
articles_with_sentiment = self.sentiment_predictor.predict_batch(
    final_articles,
    batch_size=16  # Increase if you have GPU memory
)

# For lower memory systems
articles_with_sentiment = self.sentiment_predictor.predict_batch(
    final_articles,
    batch_size=4  # Decrease if getting OOM errors
)
```

### 3. Caching

The data fetching and preprocessing are cached, but model predictions are not. This ensures fresh predictions but can be optimized:

**Option A**: Cache predictions (modify `server.py`):
```python
# Add prediction cache
self.prediction_cache = {}

# In analyze_company():
cache_key = f"{company_name}_predictions"
if cache_key in self.prediction_cache:
    return self.prediction_cache[cache_key]

result = self.financial_analyzer.analyze_news(...)
self.prediction_cache[cache_key] = result
```

## Monitoring & Logging

The integration provides detailed console logs:

```
✓ Cache hit for 'NVIDIA'
250
Initializing Similarity Expansion Pipeline...
  Model loading time: 0.523s
  ✓ Pipeline initialized in 0.842s

================================================================================
STEP 4: SENTIMENT PREDICTION
================================================================================
🔮 Running sentiment prediction on 15 articles...
  Processed 15/15 articles...
✓ Sentiment prediction completed in 1.23s
  Average: 0.082s per article

================================================================================
STEP 5: KEYPHRASE ANALYSIS
================================================================================
  Analyzed 5/15 articles...
  Analyzed 10/15 articles...
  Analyzed 15/15 articles...
✓ Keyphrase analysis completed for 15 articles

✓ Request completed for 'NVIDIA' | Total Latency: 8.456s
```

## Testing Individual Components

### Test Sentiment Predictor

```python
from src.sentiment_predictor import SentimentPredictor

predictor = SentimentPredictor()
text = "NVIDIA reports record revenue driven by AI chip demand"
prediction = predictor.predict_single(text)
print(prediction)
# Output: <senti>Good<reason>Record revenue indicates strong...
```

### Test Keyphrase Analyzer

```python
from src.keyphrase_analyzer import KeyphraseAnalyzer

analyzer = KeyphraseAnalyzer()
result = analyzer.analyze_source_with_sentiment(
    source="NVIDIA announces new AI chips",
    sentiment="<senti>Good<reason>Innovation in AI market"
)
print(result['keyphrases']['positive'])
```

## Troubleshooting

### Issue: "Model directory not found"
**Solution**: Download or ensure model files are in `model/Flan_T5_Base/`

### Issue: "CUDA out of memory"
**Solution**: Reduce batch_size or use CPU:
```python
# Force CPU usage
self.device = "cpu"
```

### Issue: Slow predictions
**Solution**: 
1. Install PyTorch with CUDA support
2. Increase batch size
3. Consider model quantization

### Issue: Server takes long to start
**Solution**: Model loading takes 2-5s, this is normal. The model is loaded once at startup.

## Next Steps

1. **Frontend Integration**: Update frontend to display sentiment and keyphrases
2. **Analytics**: Track sentiment trends over time
3. **Alerts**: Set up notifications for significant sentiment changes
4. **Optimization**: Implement prediction caching for faster responses

## Summary

✅ **Integration Complete**
- Flan-T5 model integrated for sentiment prediction
- Keyphrase analyzer categorizes article content
- Server returns enriched data with sentiment and keyphrases
- All components work seamlessly together

✅ **Ready for Production**
- Error handling implemented
- Performance optimized with batching
- Comprehensive logging for monitoring
- Graceful fallbacks on failures

✅ **Fully Backward Compatible**
- Existing API structure unchanged
- Only adds new fields to response
- Frontend can progressively adopt new features
