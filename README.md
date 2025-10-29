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


## 📄 License

MIT License - see LICENSE file for details.
