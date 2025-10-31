# AI6127-DNN: Financial News Analysis with Deep Learning

A comprehensive NLP project for stock analysis using financial news data, web scraping, and fine-tuned reasoning models.

## Notion Link: https://www.notion.so/NLP-260db05c79c58041b9b9d8552e6cbad3?source=copy_link

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

## News Sentiment Data Generator

The project includes a real-time news sentiment generator (`src/generate_synthetic_data.py`) that fetches AI company news and generates sentiment-classified data using the DeepSeek v3 API with web search capabilities.

📖 **[View Complete Usage Guide →](src/README_SENTIMENT_GENERATOR.md)**

### Setup

1. Ensure your `.env` file contains the DeepSeek API key:
   ```
   deepseeker_api_key=your_api_key_here
   ```

2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

### Usage

Generate sentiment-classified news data in CSV format:

```powershell
# Fetch 10 recent news items (default) - creates new file or appends to existing
python .\src\generate_synthetic_data.py

# Fetch custom number of news items
python .\src\generate_synthetic_data.py --n 20 --out .\data\my_sentiment_data.csv

# Focus on specific companies
python .\src\generate_synthetic_data.py --n 15 --companies NVIDIA Microsoft OpenAI
```

**Note:** The script automatically **appends** new data to existing CSV files. The header is only written when creating a new file. This allows you to continuously accumulate news data over multiple runs.

### Output Format

The script generates a CSV file with three columns:

1. **source_name**: The publication name (e.g., Reuters, Bloomberg, TechCrunch)
2. **source**: A comprehensive 3-5 sentence summary of the full article content
3. **sentiment**: Formatted as `<senti>Good/Bad/Neutral<reason>analysis`

Example CSV output:
```csv
source_name,source,sentiment
Reuters,"NVIDIA announced record quarterly earnings with data center revenue surging 409% year-over-year to $18.4 billion, driven by massive demand for its AI chips. The company provided strong forward guidance that exceeded analyst expectations.",<senti>Good<reason>Exceptional earnings beat demonstrates NVIDIA's dominant position in the AI chip market
The Information,"OpenAI is in early talks to raise new funding at a valuation of $100 billion or more. The potential funding round comes as the company continues to develop more advanced AI models.",<senti>Good<reason>Massive valuation increase signals strong investor confidence in OpenAI's growth potential
Bloomberg,"Tesla delays rollout of Full Self-Driving version 12 due to regulatory hurdles and technical challenges. The company is working with regulators to address safety concerns.",<senti>Bad<reason>Delays in key AI product launch may disappoint investors and impact revenue timeline
```

### Features

- **Real-time News**: Fetches latest news articles via DeepSeek API with web search
- **Article Summarization**: Reads full articles and generates comprehensive 3-5 sentence summaries
- **Source Attribution**: Captures publication names (Reuters, Bloomberg, etc.)
- **Automated Sentiment Classification**: AI-powered sentiment analysis (Good/Bad/Neutral)
- **Structured Output**: Clean CSV format with three columns for easy analysis
- **Append Mode**: Continuously accumulates data across multiple runs
- **Customizable**: Configurable company list and sample size
- **Metadata Tracking**: Tracks source publications and generation details

### API Details

The script uses the DeepSeek v3 model (`deepseek-v3-1-250821`) with:
- Web search capability for real-time news retrieval
- Temperature: 0.7 for balanced creativity
- Max tokens: 2000 for comprehensive responses
- Endpoint: `https://ark.ap-southeast.bytepluses.com/api/v3/chat/completions`

## 📄 License

MIT License - see LICENSE file for details.
