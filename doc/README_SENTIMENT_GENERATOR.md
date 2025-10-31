# AI Stock News Sentiment Generator

A real-time news sentiment data generator that fetches AI company news articles and generates sentiment-classified data using the DeepSeek v3 API with web search capabilities.

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Usage](#usage)
- [Output Format](#output-format)
- [Examples](#examples)
- [Understanding the Output](#understanding-the-output)
- [Tips and Best Practices](#tips-and-best-practices)
- [Troubleshooting](#troubleshooting)

---

## Features

✨ **Real-time News Fetching**: Searches the web for latest AI company news articles  
📰 **Article Summarization**: Reads full articles and generates comprehensive 3-5 sentence summaries  
🏢 **Source Attribution**: Captures publication names (Reuters, Bloomberg, TechCrunch, etc.)  
🎯 **Sentiment Classification**: AI-powered analysis (Good/Bad/Neutral) for stock impact  
📊 **CSV Output**: Clean, structured data with three columns  
➕ **Append Mode**: Continuously accumulates data across multiple runs  
⚙️ **Customizable**: Configure company list and sample size  

---

## Prerequisites

- Python 3.7 or higher
- DeepSeek API key (stored in `.env` file)
- Required Python packages (see [Setup](#setup))

---

## Setup

### 1. Install Dependencies

Make sure you have all required packages installed:

```powershell
pip install -r requirements.txt
```

Required packages:
- `requests` - For API calls
- `python-dotenv` - For environment variable management

### 2. Configure API Key

Create or edit the `.env` file in the project root directory:

```env
deepseeker_api_key=your_api_key_here
```

> **Important**: Keep your API key secret. Never commit the `.env` file to version control.

---

## Usage

### Basic Command

```powershell
python .\src\generate_synthetic_data.py
```

This will:
- Fetch 10 news items (default)
- Output to `data/ai_stock_sentiment.csv`
- Focus on default AI companies

### Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--n` | Number of news items to fetch | 10 |
| `--out` | Output CSV file path | `data/ai_stock_sentiment.csv` |
| `--companies` | Space-separated list of companies | See [Default Companies](#default-companies) |

### Default Companies

The script monitors these AI-related companies by default:
- OpenAI
- NVIDIA
- Google
- Microsoft
- Meta
- Amazon
- Intel
- AMD
- Palantir
- C3.ai
- Anthropic
- Tesla

---

## Output Format

The script generates a **CSV file** with three columns:

### Column Descriptions

| Column | Description | Example |
|--------|-------------|---------|
| **source_name** | Publication name | `Reuters`, `Bloomberg`, `The Information` |
| **source** | 3-5 sentence article summary | Full article content summary |
| **sentiment** | `<senti>sentiment<reason>analysis` | `<senti>Good<reason>Strong earnings beat...` |

### Sample CSV Output

```csv
source_name,source,sentiment
Reuters,"NVIDIA announced record quarterly earnings with data center revenue surging 409% year-over-year to $18.4 billion, driven by massive demand for its AI chips. The company provided strong forward guidance that exceeded analyst expectations. CEO Jensen Huang stated that accelerated computing and generative AI have hit the tipping point.",<senti>Good<reason>Exceptional earnings beat demonstrates NVIDIA's dominant position in the AI chip market
Bloomberg,"Google announced it is rebranding its Bard AI chatbot to Gemini and launching a new paid subscription service. The company revealed plans to integrate Gemini into its core products including Search and Gmail. This represents Google's most aggressive push into consumer AI services.",<senti>Good<reason>Monetization strategy through premium subscriptions could drive new revenue streams
The Information,"OpenAI is in early talks to raise new funding at a valuation of $100 billion or more. The potential funding round comes as the company continues to develop more advanced AI models and expand enterprise offerings.",<senti>Good<reason>Massive valuation increase signals strong investor confidence in growth potential
```

---

## Examples

### Example 1: Fetch 20 News Items

```powershell
python .\src\generate_synthetic_data.py --n 20
```

**Result**: Fetches 20 articles and saves to default output file.

### Example 2: Custom Output File

```powershell
python .\src\generate_synthetic_data.py --n 15 --out .\data\weekly_sentiment.csv
```

**Result**: Fetches 15 articles and saves to `data/weekly_sentiment.csv`.

### Example 3: Focus on Specific Companies

```powershell
python .\src\generate_synthetic_data.py --n 10 --companies NVIDIA OpenAI Microsoft
```

**Result**: Fetches 10 articles focusing only on NVIDIA, OpenAI, and Microsoft.

### Example 4: Build a Dataset Over Time

**Day 1:**
```powershell
python .\src\generate_synthetic_data.py --n 10 --out .\data\monthly_data.csv
```
*Creates file with 11 lines (1 header + 10 data rows)*

**Day 2:**
```powershell
python .\src\generate_synthetic_data.py --n 10 --out .\data\monthly_data.csv
```
*Appends 10 more rows (now 21 total lines)*

**Day 3:**
```powershell
python .\src\generate_synthetic_data.py --n 10 --out .\data\monthly_data.csv
```
*Appends 10 more rows (now 31 total lines)*

---

## Understanding the Output

### Sentiment Values

The `sentiment` column uses a structured format:

```
<senti>Good/Bad/Neutral<reason>detailed analysis
```

#### Sentiment Categories

- **Good**: Positive news likely to increase stock price
  - Examples: Strong earnings, new partnerships, product launches
  
- **Bad**: Negative news likely to decrease stock price
  - Examples: Layoffs, regulatory issues, missed targets
  
- **Neutral**: News with unclear or balanced impact
  - Examples: Routine announcements, mixed signals

### Reading the CSV in Python

```python
import pandas as pd

# Load the CSV
df = pd.read_csv('data/ai_stock_sentiment.csv')

# Display first few rows
print(df.head())

# Count sentiment distribution
sentiment_counts = df['sentiment'].str.extract(r'<senti>(\w+)<')[0].value_counts()
print(sentiment_counts)

# Filter for specific publication
reuters_news = df[df['source_name'] == 'Reuters']
```

### Reading the CSV in Excel

1. Open Excel
2. Go to **Data** → **From Text/CSV**
3. Select your CSV file
4. Excel will automatically detect columns
5. Click **Load**

---

## Tips and Best Practices

### 1. Avoid Duplicates

The API may fetch similar news across different runs. To minimize duplicates:
- Space out your data collection runs (e.g., daily vs. hourly)
- Focus on specific companies for targeted data
- Use different output files for different time periods

### 2. Optimal Sample Size

- **Small datasets (exploration)**: `--n 5` to `--n 10`
- **Regular monitoring**: `--n 10` to `--n 20`
- **Large datasets**: Multiple runs of `--n 20` (API limit considerations)

### 3. Rate Limiting

Be mindful of API usage:
- The DeepSeek API has rate limits
- Allow a few seconds between consecutive runs
- For large datasets, use multiple smaller runs

### 4. Data Quality

- Review the first few outputs to ensure quality
- Check that article summaries are comprehensive (not just headlines)
- Verify sentiment classifications align with article content

### 5. Organizing Output Files

Create a file naming strategy:
```powershell
# Daily files
python .\src\generate_synthetic_data.py --n 20 --out .\data\sentiment_2025_10_31.csv

# Weekly aggregation
python .\src\generate_synthetic_data.py --n 50 --out .\data\week_44_2025.csv

# Company-specific
python .\src\generate_synthetic_data.py --n 15 --companies NVIDIA --out .\data\nvidia_news.csv
```

---

## Troubleshooting

### Error: API Key Not Found

```
ValueError: deepseeker_api_key not found in .env file
```

**Solution**: 
1. Create a `.env` file in the project root
2. Add: `deepseeker_api_key=your_key_here`
3. Make sure the file is named exactly `.env` (with the dot)

### Error: Permission Denied

```
PermissionError: [Errno 13] Permission denied
```

**Solution**: 
- Close the CSV file if it's open in Excel or another program
- Make sure you have write permissions to the output directory

### Warning: No Valid News Items Found

```
Warning: No valid news items found in API response.
```

**Solution**: 
- Check your internet connection
- Verify API key is valid
- Try reducing `--n` to a smaller number
- Check if the company names are spelled correctly

### API Call Failed

```
RuntimeError: API call failed with status 401
```

**Solution**: 
- Verify your API key is correct and active
- Check if your API subscription is active
- Ensure you haven't exceeded rate limits

### Empty or Incomplete Summaries

If article summaries are too brief or just headlines:

**Solution**: 
- The API may not have full access to some articles
- Try running again - different sources may be fetched
- Check the raw API response in debug output

---

## Output Statistics

To check your accumulated data:

### Count Total Articles
```powershell
(Get-Content .\data\ai_stock_sentiment.csv | Measure-Object -Line).Lines - 1
```
*(Subtracts 1 for the header row)*

### View Column Headers
```powershell
Get-Content .\data\ai_stock_sentiment.csv | Select-Object -First 1
```

### Check File Size
```powershell
(Get-Item .\data\ai_stock_sentiment.csv).Length / 1KB
```
*(Shows size in KB)*

---

## API Details

### Model Information
- **Model**: `deepseek-v3-1-250821`
- **Endpoint**: `https://ark.ap-southeast.bytepluses.com/api/v3/chat/completions`
- **Features**: Web search, article reading, sentiment analysis
- **Temperature**: 0.7 (balanced creativity)
- **Max Tokens**: 2000 (comprehensive responses)

### Data Flow
1. Script sends request to DeepSeek API with company list
2. API searches the web for recent news articles
3. API reads full articles and generates summaries
4. API classifies sentiment and provides analysis
5. Script parses response and writes to CSV
6. Data is appended to existing file (or new file created)

---

## Support and Feedback

For issues, questions, or suggestions:
- Check the main project README: `../README.md`
- Review API documentation: DeepSeek API docs
- Ensure all dependencies are up to date: `pip install -r requirements.txt --upgrade`

---

## Version History

- **v2.0** (Oct 2025): Added three-column format with source names and article summaries
- **v1.1** (Oct 2025): Implemented append mode for continuous data collection
- **v1.0** (Oct 2025): Initial release with basic sentiment generation

---

## Quick Reference Card

### Most Common Commands

```powershell
# Basic usage (10 articles, default file)
python .\src\generate_synthetic_data.py

# Fetch 20 articles
python .\src\generate_synthetic_data.py --n 20

# Custom output file
python .\src\generate_synthetic_data.py --out .\data\my_data.csv

# Specific companies
python .\src\generate_synthetic_data.py --companies NVIDIA OpenAI

# Daily collection routine
python .\src\generate_synthetic_data.py --n 15 --out .\data\daily_$(Get-Date -Format yyyy_MM_dd).csv
```

### File Locations

- **Script**: `src/generate_synthetic_data.py`
- **Config**: `.env` (in project root)
- **Default Output**: `data/ai_stock_sentiment.csv`
- **This Guide**: `src/README_SENTIMENT_GENERATOR.md`

### Column Structure

```
source_name  |  source (summary)  |  sentiment (<senti>...<reason>...)
```

---

**Happy Data Collecting! 📊🚀**
