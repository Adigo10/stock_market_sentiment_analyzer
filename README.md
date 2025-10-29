# Rule based ranking of the articles based on **recency** and **event magnitude** 


### Recency Scoring
Recent articles are given higher importance using an **exponential decay formula**:

score = e^(-decay_rate × days_old)

- Default decay rate = 0.1 (10% decay per day)
- Example:
  - Today → 1.00
  - 10 days old → 0.37
  - 30 days old → 0.05

---

### Event Magnitude Scoring
Articles are classified by **keyword-based event detection**, but **high- and medium-impact keywords are only considered if they appear alongside relevant entities**:

- Recognized entities: `ORG`, `PRODUCT`, `PERSON`  
- Low-impact keywords are applied without entity filtering  

| Impact Level | Example Keywords | Score Range |
|-------------|----------------|------------|
| High        | earnings, merger, acquisition, bankruptcy, CEO, lawsuit | 0.8 – 0.95 |
| Medium      | partnership, contract, product launch, rating, deal | 0.4 – 0.6 |
| Low         | commentary, outlook, update, report, expects | 0.2 – 0.3 |

> NER ensures that impactful keywords are tied to **relevant companies, products, or people**, improving ranking accuracy.

---
### Final Rank Score
Each article’s rank score is a weighted combination of recency and magnitude:

rank_score = 0.4 * recency_score + 0.6 * event_magnitude_score

This score is then used to **sort and rank all articles**.

---

## Input Format
Input is a JSON file containing a list of news articles with at least these fields:

```json
[
    {
    "id": 2001,
    "category": "technology",
    "datetime": 1767446400,
    "headline": "Google under EU investigation for data privacy issues in Gemini AI model",
    "summary": "The European Commission launched an investigation into Google's Gemini AI citing concerns over data collection and transparency.",
    "source": "Google",
    "image": "https://example.com/images/google-ai.jpg",
    "related": "",
    "url": "https://www.google.com/news/2025/10/30/google-gemini-investigation"
  }
]

```
## Output Format
output.json contains "rank_score", "recency_score" and "magnitude_score" in addition to the exisitng metadata

```json
[
    {
        "id":2010,
        "category":"technology",
        "datetime":1767441600,
        "headline":"Broadcom CEO comments on semiconductor market stabilization",
        "summary":"Broadcom CEO Hock Tan noted signs of supply chain normalization and steady enterprise chip demand for 2026.",
        "source":"Broadcom",
        "image":"https:\/\/example.com\/images\/broadcom-ceo.jpg",
        "related":"",
        "url":"https:\/\/www.broadcom.com\/news\/2025\/10\/market-stabilization",
        "rank_score":0.91,
        "recency_score":1.0,
        "magnitude_score":0.85
    }
]

```

## Installation

install dependencies and spaCy languag model
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Notes
- High- and medium-impact keywords are filtered by relevant NER entities (ORG, PRODUCT, PERSON)
- Low-impact keywords are applied to all text without entity filtering
- Handles all kinds of datetime formats: UNIX timestamps, ISO 8601 strings, or other string formats
