import sys
from pathlib import Path
import pandas as pd

current_dir = Path(__file__).parent.absolute()
src_path = current_dir / 'src'
sys.path.insert(0, str(src_path))

from src.rule_based_ranker import FinancialNewsRanker


class FinancialNewsAnalyzer:
    
    def __init__(self, decay_rate: float = 0.1):
        self.ranker = FinancialNewsRanker(decay_rate=decay_rate)
    
    def rank_articles(self, news_data: dict, top_n: int = None) -> pd.DataFrame:
        """Analyze and rank news. Returns DataFrame with ranked articles."""
        df = pd.DataFrame(news_data["unique_news"])
        ranked_df = self.ranker.rank_articles(df, top_n=top_n)
        self.ranker.print_ranking_summary(ranked_df.head(5))
        return ranked_df
    
    def analyze_news(self, news_data: dict) -> list:
        """
        This function will be called from server.py
        Add all models and return final result.
        """
        ranked_df = self.rank_articles(news_data)
        
        ## change ranked articles to reasoning output and return final result from here
        return ranked_df[:5].to_dict(orient='records')