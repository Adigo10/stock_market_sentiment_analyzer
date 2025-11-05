# 🤖 AI Stock Market Sentiment Analyzer

Complete end-to-end financial news analysis system powered by AI, featuring sentiment prediction and keyphrase extraction.

## ✨ Features

- **🔍 Real-time News Fetching**: Automatically fetches latest financial news
- **📊 Rule-Based Ranking**: Intelligent article ranking algorithm
- **🤝 Similarity Expansion**: Semantic similarity-based article selection
- **🤖 AI Sentiment Prediction**: Fine-tuned Flan-T5 model for sentiment analysis
- **🔑 Keyphrase Extraction**: Automatic extraction and categorization of key phrases
- **💾 Smart Caching**: Caches preprocessed data for faster subsequent requests
- **🎨 Beautiful UI**: Modern, responsive Streamlit frontend

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND (Streamlit)                    │
│  • Company selection                                          │
│  • Real-time analysis dashboard                              │
│  • Sentiment visualization                                   │
│  • Keyphrase display                                         │
└─────────────────────────────────────────────────────────────┘
                              ↓ HTTP
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND API (FastAPI)                     │
│  • /analyze-company  - Main analysis endpoint                │
│  • /companies        - List supported companies              │
│  • /health          - Health check                           │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    ANALYSIS PIPELINE                         │
│  1. Data Fetching & Preprocessing (Cached)                   │
│  2. Rule-Based Ranking                                       │
│  3. Similarity Expansion                                     │
│  4. Sentiment Prediction (Flan-T5)                          │
│  5. Keyphrase Analysis                                       │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Virtual environment
- GROQ API key (for similarity expansion)

### Installation

```bash
# 1. Clone the repository
git clone <repository-url>
cd stock_market_sentiment_analyzer

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Download NLTK data
python setup_nltk.py

# 6. Set up environment variables
# Create .env file with:
GROQ_API_KEY=your_api_key_here
```

### Running the Application

#### Option 1: Using the Startup Script (Windows)

```bash
start.bat
```

This will automatically start both the backend server and frontend UI.

#### Option 2: Manual Start

```bash
# Terminal 1: Start backend
python server.py

# Terminal 2: Start frontend
streamlit run frontend.py
```

### Accessing the Application

- **Frontend UI**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📖 Usage

1. **Open the Frontend**: Navigate to http://localhost:8501
2. **Select Company**: Choose a company from the dropdown
3. **Analyze**: Click the "🚀 Analyze" button
4. **View Results**: See sentiment analysis and keyphrases for top 15 articles

## 🎨 Frontend Features

### Dashboard Components

1. **Analysis Summary Cards**
   - Positive sentiment count (green)
   - Negative sentiment count (red)
   - Neutral sentiment count (gray)
   - Total keyphrases extracted

2. **Article Cards** (for each article)
   - Headline with sentiment badge
   - Publication date and rank score
   - Article summary
   - AI sentiment analysis explanation
   - Color-coded keyphrases (positive/negative/neutral)
   - Link to full article

### Visual Elements

- **Sentiment Badges**: Color-coded indicators (🟢 Positive, 🔴 Negative, ⚪ Neutral)
- **Keyphrase Pills**: Categorized and color-coded key phrases
- **Gradient Cards**: Modern card-based layout with shadows
- **Responsive Design**: Works on desktop and tablet

## 🔧 API Endpoints

### POST /analyze-company

Analyze financial news for a specific company.

**Request:**
```json
{
  "company_name": "NVIDIA"
}
```

**Response:**
```json
{
  "company_name": "NVIDIA",
  "status": "success",
  "result": [
    {
      "headline": "...",
      "summary": "...",
      "url": "...",
      "publish_date": "...",
      "rank_score": 0.95,
      "predicted_sentiment": "<senti>Good<reason>Strong revenue growth...",
      "keyphrase_analysis": {
        "overall_sentiment": "good",
        "sentiment_reason": "...",
        "keyphrases": {
          "positive": [...],
          "negative": [...],
          "neutral": [...]
        },
        "summary": {
          "positive_count": 8,
          "negative_count": 2,
          "neutral_count": 5
        }
      }
    }
  ]
}
```

### GET /companies

Get list of supported companies.

**Response:**
```json
{
  "companies": ["NVIDIA", "AMD", "Intel", ...],
  "total": 20
}
```

### GET /health

Health check for all system components.

**Response:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "components": {
    "data_fetcher": "operational",
    "sentiment_predictor": "operational (cuda)",
    "keyphrase_analyzer": "operational"
  }
}
```

## 📊 Pipeline Details

### 1. Data Fetching & Preprocessing
- Fetches news from financial APIs
- Deduplicates articles
- Cleans and normalizes text
- Results cached for 24 hours

### 2. Rule-Based Ranking
- Scores articles based on:
  - Recency
  - Company relevance
  - Source credibility
  - Content quality

### 3. Similarity Expansion
- Uses sentence transformers (all-mpnet-base-v2)
- Computes semantic similarity
- Expands to top 15 most relevant articles

### 4. Sentiment Prediction
- Fine-tuned Flan-T5 Base model
- Predicts: Good/Bad/Neutral
- Generates explanation for sentiment
- Batch processing for efficiency

### 5. Keyphrase Analysis
- Extracts noun phrases, entities, technical terms
- Categorizes as positive/negative/neutral
- Assigns confidence scores
- Uses NLTK + pattern matching

## ⚙️ Configuration

### Server Configuration (server.py)

- **Host**: 0.0.0.0
- **Port**: 8000
- **Timeout**: 300 seconds
- **Max Articles**: 250 (configurable)

### Frontend Configuration (frontend.py)

- **API Base URL**: http://localhost:8000
- **Request Timeout**: 120 seconds
- **Layout**: Wide mode

### Model Configuration (model_pipeline.py)

- **Similarity Model**: all-mpnet-base-v2
- **Similarity Threshold**: 0.6
- **Top K**: 10
- **Batch Size**: 8 (for predictions)

## 🐛 Troubleshooting

### Server won't start

**Issue**: Model directory not found
```
Solution: Ensure model/Flan_T5_Base/ exists with all required files
```

**Issue**: CUDA out of memory
```
Solution: Reduce batch_size in model_pipeline.py or use CPU
```

### Frontend can't connect

**Issue**: Connection refused
```
Solution: Ensure backend server is running on port 8000
```

**Issue**: Request timeout
```
Solution: Increase timeout in frontend.py (currently 120s)
```

### NLTK errors

**Issue**: Resource 'punkt_tab' not found
```
Solution: Run python setup_nltk.py
```

## 📈 Performance

### First Request (Cold Start)
- Model loading: 2-5 seconds
- Data fetching: 2-5 seconds
- Processing: 3-8 seconds
- **Total**: ~10-20 seconds

### Subsequent Requests (Cached)
- Data retrieval: <0.1 seconds
- Processing: 3-8 seconds
- **Total**: ~3-8 seconds

### Optimization Tips
1. Use GPU for 5-10x faster inference
2. Enable prediction caching for repeated queries
3. Reduce batch size on low-memory systems
4. Pre-warm cache for frequently queried companies

## 🔐 Security

- API keys stored in `.env` file (not committed)
- Input validation on all endpoints
- Rate limiting recommended for production
- CORS configured for localhost development

## 📝 File Structure

```
stock_market_sentiment_analyzer/
├── server.py                 # FastAPI backend server
├── frontend.py              # Streamlit frontend UI
├── model_pipeline.py        # Main analysis pipeline
├── start.bat               # Windows startup script
├── setup_nltk.py           # NLTK data downloader
├── test_integration.py     # Integration tests
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
├── src/
│   ├── sentiment_predictor.py    # Flan-T5 model wrapper
│   ├── keyphrase_analyzer.py     # Keyphrase extraction
│   ├── fetch_data.py              # News fetching
│   ├── data_process.py            # Data preprocessing
│   ├── rule_based_ranker.py       # Article ranking
│   └── cache_manager.py           # Caching system
├── model/
│   └── Flan_T5_Base/             # Fine-tuned T5 model
├── pipeline/
│   └── pipeline.py               # Similarity expansion
└── doc/
    ├── MODEL_INTEGRATION.md      # Integration docs
    └── QUICK_START_INTEGRATION.md # Quick start guide
```

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

See LICENSE file for details.

## 🙏 Acknowledgments

- **Flan-T5**: Google's fine-tuned T5 model
- **Sentence Transformers**: SBERT for semantic similarity
- **FastAPI**: Modern Python web framework
- **Streamlit**: Beautiful data app framework
- **NLTK**: Natural language processing toolkit

## 📞 Support

For issues or questions:
1. Check troubleshooting section
2. Review documentation in `/doc`
3. Open an issue on GitHub
4. Check API health endpoint: http://localhost:8000/health

---

**Version**: 2.0.0  
**Last Updated**: November 4, 2025  
**Status**: ✅ Production Ready
