import pandas as pd
import numpy as np
import json
from datetime import datetime
from datetime import timezone
import re
import spacy


class FinancialNewsRanker:
    def __init__(self, decay_rate=0.1):
        """
        Initialize the ranker with configurable parameters.
        """
        self.decay_rate = decay_rate

        # Load spaCy model
        self.nlp = spacy.load("en_core_web_sm")

        
        # Event magnitude keywords with impact scores
        self.high_impact_keywords = {
            'earnings': 0.95, 'merger': 0.95, 'acquisition': 0.95, 'acquires': 0.95,
            'bankruptcy': 0.90, 'bankrupt': 0.90, 'ceo': 0.85, 'chief executive': 0.85,
            'lawsuit': 0.80, 'regulatory': 0.85, 'fda approval': 0.95, 'fda approves': 0.95,
            'stock split': 0.85, 'dividend': 0.80, 'restructuring': 0.85,
            'investigation': 0.80, 'fraud': 0.90, 'recall': 0.85,
            'guidance': 0.85, 'forecast': 0.80, 'layoffs': 0.85, 'layoff': 0.85
        }
        
        self.medium_impact_keywords = {
            'partnership': 0.60, 'contract': 0.55, 'product launch': 0.60,
            'launches': 0.55, 'upgrade': 0.50, 'downgrade': 0.50,
            'rating': 0.45, 'analyst': 0.40, 'expansion': 0.55,
            'investment': 0.50, 'funding': 0.55, 'deal': 0.50,
            'collaboration': 0.50, 'agreement': 0.50
        }
        
        self.low_impact_keywords = {
            'commentary': 0.30, 'outlook': 0.30, 'analysis': 0.25,
            'opinion': 0.20, 'update': 0.25, 'report': 0.25,
            'expects': 0.30, 'could': 0.20, 'may': 0.20
        }
        
        self.weights = {'recency': 0.40, 'magnitude': 0.60}  # final score weights

    # ------------------ Column Auto-Detection ------------------
    def auto_detect_columns(self, df):
        """
        Detect date, headline, and summary columns automatically.
        """
        date_cols = ['date', 'datetime', 'published', 'timestamp', 'time']
        headline_cols = ['headline', 'title', 'head']
        summary_cols = ['summary', 'desc', 'description', 'content']

        date_col = next((c for c in date_cols if c in df.columns), None)
        headline_col = next((c for c in headline_cols if c in df.columns), None)
        summary_col = next((c for c in summary_cols if c in df.columns), None)

        if not date_col or not headline_col or not summary_col:
            raise ValueError("Could not automatically detect required columns in the dataset.")
        
        return date_col, headline_col, summary_col

    # ------------------ Recency Score ------------------
    from datetime import timezone

    def calculate_recency_score(self, date_value, reference_date=None):
        if reference_date is None:
            reference_date = datetime.now(timezone.utc)  # make reference date UTC-aware

        # Handle UNIX timestamp
        if isinstance(date_value, (int, float)):
            article_date = datetime.fromtimestamp(date_value, tz=timezone.utc)

        # Handle string date
        elif isinstance(date_value, str):
            try:
                article_date = pd.to_datetime(date_value, utc=True)  # parse and set UTC
            except:
                return 0.5

        # Handle datetime object
        elif isinstance(date_value, datetime):
            # If naive, make UTC
            if date_value.tzinfo is None:
                article_date = date_value.replace(tzinfo=timezone.utc)
            else:
                article_date = date_value.astimezone(timezone.utc)
        else:
            return 0.5

        # Calculate days difference
        days_old = max(0, (reference_date - article_date).days)
        return np.exp(-self.decay_rate * days_old)

    # ------------------ Magnitude Score ------------------
    def calculate_magnitude_score(self, text):
        text_lower = text.lower()
        max_score = 0.0
        
        doc = self.nlp(text)
        entities = [ent.text.lower() for ent in doc.ents if ent.label_ in ['ORG', 'PRODUCT', 'PERSON']]

        # High impact keywords
        for kw, score in self.high_impact_keywords.items():
            if kw in text_lower and any(ent in text_lower for ent in entities):
                max_score = max(max_score, score)

        # Medium impact keywords if high not triggered
        if max_score < 0.8:
            for kw, score in self.medium_impact_keywords.items():
                if kw in text_lower and any(ent in text_lower for ent in entities):
                    max_score = max(max_score, score)

        # Low impact keywords unchanged
        if max_score < 0.4:
            for kw, score in self.low_impact_keywords.items():
                if kw in text_lower:
                    max_score = max(max_score, score)
        return max_score if max_score>0 else 0.15


    # ------------------ rank Score ------------------
    def calculate_rank_score(self, row, date_col, headline_col, summary_col):
        text = f"{row.get(headline_col, '')} {row.get(summary_col, '')}"
        recency = self.calculate_recency_score(row[date_col])
        magnitude = self.calculate_magnitude_score(text)
        rank = self.weights['recency'] * recency + self.weights['magnitude'] * magnitude
        return {'rank_score': rank, 'recency_score': recency, 'magnitude_score': magnitude}

    # ------------------ Rank Articles ------------------
    def rank_articles(self, df, top_n=None):
        date_col, headline_col, summary_col = self.auto_detect_columns(df)

        scores = df.apply(
            lambda row: self.calculate_rank_score(row, date_col, headline_col, summary_col),
            axis=1, result_type='expand'
        )

        ranked_df = pd.concat([df, scores], axis=1)
        ranked_df = ranked_df.sort_values('rank_score', ascending=False)

        if top_n:
            ranked_df = ranked_df.head(top_n)
        return ranked_df

    # ------------------ Print Summary ------------------
    def print_ranking_summary(self, ranked_df):
        print("=" * 100)
        print(f"{'RANK':<6} {'SCORE':<8} {'HEADLINE':<60} {'DATE':<12}")
        print("=" * 100)
        for idx, (_, row) in enumerate(ranked_df.iterrows(), 1):
            headline = row.get('headline', '')[:57] + "..." if len(row.get('headline', '')) > 60 else row.get('headline', '')
            date_val = row.get('date', row.get('datetime', ''))
            print(f"{idx:<6} {row['rank_score']:.4f}   {headline:<60} {str(date_val):<12}")
            print(f"       Recency: {row['recency_score']:.3f} | Magnitude: {row['magnitude_score']:.3f}")
            print("-" * 100)

# ------------------ Example Usage ------------------
if __name__ == "__main__":
    # Load JSON
    with open("../processed_output.json", "r") as f:
        data = json.load(f)

    df = pd.DataFrame(data["unique_news"])

    ranker = FinancialNewsRanker(decay_rate=0.1)
    ranked_articles = ranker.rank_articles(df, top_n=None)  # rank all

    # Save ranked results
    ranked_articles.to_json("ranked_articles.json", orient="records", indent=4, date_format="iso")
    print("\nRanked dataset saved to 'ranked_articles.json'")

    # Print top 5 summary
    ranker.print_ranking_summary(ranked_articles.head(5))
