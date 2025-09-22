# AI6127-DNN: Financial News Analysis with Deep Learning

A comprehensive NLP project for stock analysis using financial news data, web scraping, and fine-tuned reasoning models.

## Project Overview

This project implements an intelligent financial news analysis system that:

1. **Scrapes Financial News**: Uses Groq API with GPT-OSS-20B and browser search to find top 10 financial news articles for any stock
2. **Processes Text Data**: Implements comprehensive text cleaning with custom financial term preservation
3. **Analyzes Sentiment**: Provides detailed sentiment analysis of financial news
4. **Generates Reasoning**: Fine-tunes models to explain why news events affect stock prices
5. **Delivers Insights**: Creates comprehensive reports and analysis summaries

#### Note: Prioritize output to JSON format, rewrite NLTK modules as custom code

## Architecture

```
AI6127-DNN/
├── src/                          # Core source code
│   ├── scrapers/                 # News scraping modules
│   ├── utils/                    # Utility modules
│   ├── models/                   # ML model modules
│   └── pipeline/                 # Main processing pipeline
├── config/                       # Configuration management
├── examples/                     # Example scripts and demos
├── data/                        # Data storage
│   ├── raw/                     # Raw scraped data
│   ├── processed/               # Cleaned data
│   └── models/                  # Trained model artifacts
├── tests/                       # Unit tests
└── docs/                        # Documentation
```

## Features

### News Scraping
- **Groq Integration**: Uses GPT-OSS-20B with browser search capabilities
- **Financial Focus**: Targets reputable financial news sources
- **Time-based Filtering**: Configurable date ranges (default: past year)
- **Parallel Processing**: Efficient multi-stock analysis

### Text Processing
- **Custom CleanText Class**: Implements full preprocessing pipeline
- **Financial Term Preservation**: Maintains important financial vocabulary
- **Multi-step Cleaning**:
  1. Lowercase normalization
  2. Noise removal (HTML, URLs, irrelevant characters)
  3. Stop word removal with tokenization
  4. Stemming using Porter/Snowball stemmers
  5. Lemmatization with WordNet
- **Concurrent Processing**: Uses `concurrent.futures` for performance

### AI Models
- **Sentiment Analysis**: Multi-class classification (positive/negative/neutral)
- **Reasoning Generation**: Fine-tuned models explain market movements
- **Question Answering**: Financial Q&A capabilities
- **Model Fine-tuning**: Custom training on domain-specific data

### Analysis Pipeline
- **End-to-end Processing**: From scraping to insights
- **Quality Scoring**: Automated analysis quality assessment
- **Comprehensive Reporting**: Detailed text and JSON outputs
- **Portfolio Analysis**: Multi-stock comparison and ranking


## Advanced Features

### Multiprocessing Optimization
- Uses `concurrent.futures.ThreadPoolExecutor` for I/O-bound tasks
- Uses `concurrent.futures.ProcessPoolExecutor` for CPU-bound tasks
- Configurable worker limits to prevent resource exhaustion

### Financial Domain Adaptation
- Custom stop word lists that preserve financial terminology
- Financial entity recognition and preservation
- Sentiment analysis tuned for financial contexts

### Quality Assurance
- Automated quality scoring for analysis results
- Comprehensive error handling and logging
- Input validation and sanitization

## 📄 License

MIT License - see LICENSE file for details.
