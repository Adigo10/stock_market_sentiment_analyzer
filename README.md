# AI6127-DNN: Financial News Analysis with Deep Learning - Text Pre-Processing

### Text Processing
- **Custom CleanText Class**: Implements full preprocessing pipeline
- **Financial Term Preservation**: Maintains important financial vocabulary
- **Multi-step Cleaning**:
  1. Lowercase normalization
  2. Noise removal (HTML, URLs, irrelevant characters)
  3. Stop word removal with tokenization
  4. Lemmatization with WordNet

### Example Input
This is what the input.json file should look like:
```
{
  "articles": [
    {
      "id": 1,
      "title": "Tesla Reports Strong Q3 Results",
      "content": "Tesla reported Q3 earnings of $2.3B, beating analyst estimates by 15%. EPS came in at $0.95 versus expected $0.87. CEO Elon Musk praised the team's execution.",
      "source": "Reuters",
      "date": "2024-10-15"
    },
    {
      "id": 2,
      "title": "Amazon Expands AWS Services",
      "content": "Amazon Web Services announced a $5B investment in new data centers across Europe. The expansion is expected to increase AWS revenue by 20% YoY.",
      "source": "Bloomberg",
      "date": "2024-10-16"
    }
  ]
}
```

### Usage Example
```
from data_process import FinancialDataCleaner 
import json

# Sample data for testing
sample_data = {
    "news": [
        {
            "id": 1,
            "title": "Tesla Reports Strong Q3 Results",
            "content": "Tesla reported Q3 earnings of $2.3B, beating analyst estimates by 15%. EPS came in at $0.95 versus expected $0.87. CEO Elon Musk praised the team's execution in the year 2025.",
            "source": "Reuters",
            "date": "2024-10-15"
        },
        {
            "id": 2,
            "title": "Apple Unveils New iPhone Model",
            "content": "Apple Inc. announced the launch of its latest iPhone model, featuring a new A16 chip and improved battery life. The new model starts at $999 and is expected to boost sales in Q4.",
            "source": "Bloomberg",
            "date": "2024-10-14"
        }
    ,
        {
            "id": 3,
            "title": "Amazon's Stock Hits Record High",
            "content": "Amazon's stock price surged to a record high of $3,500 per share, driven by strong holiday sales and positive earnings reports. Analysts predict continued growth in the e-commerce giant's market share.",
            "source": "CNBC",
            "date": "2024-10-13"
        }
        ]}
# Save sample
with open('sample_news.json', 'w') as f:
    json.dump(sample_data, f, indent=2)

# Process with currency/percentage removal
cleaner = FinancialDataCleaner()

result = cleaner.process_json_file(
    input_file='sample_news.json',
    output_file='cleaned_news.json')
```


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
