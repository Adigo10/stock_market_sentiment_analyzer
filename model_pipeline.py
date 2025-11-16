import sys
from pathlib import Path
import pandas as pd
import json
import tempfile
import os

current_dir = Path(__file__).parent.absolute()
src_path = current_dir / "src"
pipeline_path = current_dir / "pipeline"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(pipeline_path))

from src.rule_based_ranker import FinancialNewsRanker
from pipeline import SimilarityExpansionPipeline


class FinancialNewsAnalyzer:

    def __init__(
        self,
        decay_rate: float = 0.1,
        similarity_threshold: float = 0.6,
        top_k: int = 10,
    ):
        self.decay_rate = decay_rate
        self.similarity_pipeline = SimilarityExpansionPipeline(
            model_name="all-mpnet-base-v2",
            similarity_threshold=similarity_threshold,
            top_k=top_k,
        )

    def rank_articles(
        self, news_data: dict, company_name: str = None, top_n: int = None
    ) -> pd.DataFrame:
        """Analyze and rank news. Returns DataFrame with ranked articles."""
        # Create ranker with target company for company-specific relevance scoring
        ranker = FinancialNewsRanker(
            decay_rate=self.decay_rate, target_company=company_name
        )

        df = pd.DataFrame(news_data["unique_news"])
        ranked_df = ranker.rank_articles(df, top_n=top_n)
        ranker.print_ranking_summary(ranked_df.head(5))
        return ranked_df

    def analyze_news(self, news_data: dict, company_name: str = None) -> list:
        """
        This function will be called from server.py
        Performs ranking followed by similarity-based expansion.
        """
        # Step 1: Rank articles using rule-based ranker with company-specific scoring
        ranked_df = self.rank_articles(news_data, company_name)

        # Step 2: Prepare data for similarity pipeline
        # Convert ranked DataFrame back to list format with rank_score
        ranked_articles = ranked_df.to_dict(orient="records")

        # Step 3: Apply similarity expansion pipeline
        try:
            # Create temporary files for the similarity pipeline
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False
            ) as temp_input:
                json.dump(ranked_articles, temp_input, ensure_ascii=False, indent=2)
                temp_input_path = temp_input.name

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False
            ) as temp_output:
                temp_output_path = temp_output.name

            # Run similarity expansion pipeline
            final_articles = self.similarity_pipeline.run(
                temp_input_path, temp_output_path
            )

            # Clean up temporary files
            os.unlink(temp_input_path)
            os.unlink(temp_output_path)

            print(
                f"✓ Similarity expansion completed. Final articles: {len(final_articles)}"
            )
            return final_articles

        except Exception as e:
            print(f"✗ Similarity expansion failed: {str(e)}")
            print("✓ Falling back to top 5 ranked articles")
            # Fallback to original behavior if similarity pipeline fails
            return ranked_df[:5].to_dict(orient="records")
