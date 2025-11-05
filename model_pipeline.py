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
from src.sentiment_predictor import SentimentPredictor
from src.keyphrase_analyzer import KeyphraseAnalyzer


class FinancialNewsAnalyzer:

    def __init__(
        self,
        decay_rate: float = 0.1,
        similarity_threshold: float = 0.6,
        top_k: int = 10,
    ):
        self.decay_rate = decay_rate
        
        try:
            self.similarity_pipeline = SimilarityExpansionPipeline(
                model_name="all-mpnet-base-v2",
                similarity_threshold=similarity_threshold,
                top_k=top_k,
            )
        except Exception as e:
            print(f"⚠️  Warning: Similarity pipeline initialization failed: {e}")
            self.similarity_pipeline = None
        
        # Initialize sentiment predictor and keyphrase analyzer
        try:
            print("Initializing Sentiment Predictor...")
            self.sentiment_predictor = SentimentPredictor()
        except Exception as e:
            print(f"✗ Failed to initialize Sentiment Predictor: {e}")
            raise
        
        try:
            print("Initializing Keyphrase Analyzer...")
            self.keyphrase_analyzer = KeyphraseAnalyzer()
        except Exception as e:
            print(f"⚠️  Warning: Keyphrase Analyzer initialization failed: {e}")
            self.keyphrase_analyzer = None

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
        Performs ranking, similarity expansion, sentiment prediction, and keyphrase analysis.
        
        Pipeline:
        1. Rank articles using rule-based ranker
        2. Apply similarity expansion to get top 15 articles
        3. Pass each article to Flan-T5 model for sentiment prediction
        4. Pass source and predicted sentiment to keyphrase analyzer
        5. Return final enriched results
        """
        # Step 1: Rank articles using rule-based ranker with company-specific scoring
        ranked_df = self.rank_articles(news_data, company_name)

        # Step 2: Prepare data for similarity pipeline
        # Convert ranked DataFrame back to list format with rank_score
        ranked_articles = ranked_df.to_dict(orient="records")

        # Step 3: Apply similarity expansion pipeline to get top 15
        if self.similarity_pipeline is not None:
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

            except Exception as e:
                print(f"✗ Similarity expansion failed: {str(e)}")
                print("✓ Falling back to top 15 ranked articles")
                # Fallback to original behavior if similarity pipeline fails
                final_articles = ranked_df[:15].to_dict(orient="records")
        else:
            print("⚠️  Similarity pipeline not available, using top 15 ranked articles")
            final_articles = ranked_df[:15].to_dict(orient="records")
        
        # Step 4: Run sentiment prediction on top 15 articles
        print(f"\n{'='*80}")
        print("STEP 4: SENTIMENT PREDICTION")
        print(f"{'='*80}")
        articles_with_sentiment = self.sentiment_predictor.predict_batch(
            final_articles,
            batch_size=8
        )
        
        # Step 5: Run keyphrase analysis on each article
        print(f"\n{'='*80}")
        print("STEP 5: KEYPHRASE ANALYSIS")
        print(f"{'='*80}")
        enriched_articles = []
        
        if self.keyphrase_analyzer is not None:
            for i, article in enumerate(articles_with_sentiment):
                try:
                    source_text = article.get('source_text', '')
                    predicted_sentiment = article.get('predicted_sentiment', '')
                    
                    # Run keyphrase analysis
                    keyphrase_result = self.keyphrase_analyzer.analyze_source_with_sentiment(
                        source=source_text,
                        sentiment=predicted_sentiment
                    )
                    
                    # Add keyphrase analysis to article
                    article['keyphrase_analysis'] = keyphrase_result
                    enriched_articles.append(article)
                    
                    if (i + 1) % 5 == 0 or (i + 1) == len(articles_with_sentiment):
                        print(f"  Analyzed {i + 1}/{len(articles_with_sentiment)} articles...")
                
                except Exception as e:
                    print(f"⚠️  Warning: Keyphrase analysis failed for article {i+1}: {e}")
                    # Still add the article without keyphrase analysis
                    enriched_articles.append(article)
            
            print(f"✓ Keyphrase analysis completed for {len(enriched_articles)} articles")
        else:
            print("⚠️  Keyphrase analyzer not available, skipping keyphrase analysis")
            enriched_articles = articles_with_sentiment
        
        return enriched_articles
