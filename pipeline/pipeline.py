import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer, util
from typing import List, Dict, Tuple
from pathlib import Path
from datetime import datetime, timezone
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

print(" Imports successful")


class SimilarityExpansionPipeline:
    """
    Complete pipeline for similarity-based article expansion.

    Workflow:
    1. Load JSON input file
    2. Identify top 5 articles (those with 'rank_score' field)
    3. Generate summaries of top 5 articles
    4. Compute cosine similarity against remaining articles
    5. Select top 10 + any above threshold (default 0.5)
    6. Output combined articles to JSON file
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        similarity_threshold: float = 0.5,
        top_k: int = 10,
        groq_api_key: str = None,
    ):
        """
        Initialize the pipeline.

        Args:
            model_name: Sentence transformer model to use
            similarity_threshold: Minimum similarity score for inclusion
            top_k: Number of top similar articles to select
            groq_api_key: Groq API key (if None, will use GROQ_API_KEY env var)
        """
        print(f" Initializing Similarity Expansion Pipeline...")
        self.model = SentenceTransformer(model_name)
        self.similarity_threshold = similarity_threshold
        self.top_k = top_k

        # Initialize Groq client
        api_key = os.getenv("GROQ_API_KEY")
        self.groq_client = Groq(api_key=api_key)

        print(f" Loaded model: {model_name}")
        print(f"   Similarity threshold: {similarity_threshold}")
        print(f"   Top-K: {top_k}")
        if self.groq_client:
            print(f"   Groq API: Enabled")
        else:
            print(f"   Groq API: Disabled (using basic summarization)")

    def load_input(self, input_file: str) -> List[Dict]:
        """Load articles from JSON file."""
        print(f"\n Loading input file: {input_file}")
        with open(input_file, "r", encoding="utf-8") as f:
            articles = json.load(f)
        print(f" Loaded {len(articles)} articles")
        return articles

    @staticmethod
    def _get_headline(article: Dict) -> str:
        return article.get("headline") or article.get("title") or ""

    @staticmethod
    def _get_text(article: Dict) -> str:
        return (
            article.get("summary")
            or article.get("content")
            or article.get("headline")
            or ""
        )

    @staticmethod
    def _get_date_str(article: Dict) -> str:
        if "datetime" in article and isinstance(article["datetime"], (int, float)):
            try:
                return datetime.fromtimestamp(
                    article["datetime"], tz=timezone.utc
                ).strftime("%Y-%m-%d")
            except Exception:
                pass
        return str(article.get("date", "N/A"))

    def separate_articles(self, articles: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        Separate articles into top 5 (highest rank_score) and remaining.

        Args:
            articles: List of all articles

        Returns:
            Tuple of (top_5_articles, remaining_articles)
        """
        print(
            f"\n Separating articles: taking top 5 by rank_score, rest as remaining..."
        )

        sorted_all = sorted(
            articles, key=lambda x: x.get("rank_score", 0.0), reverse=True
        )

        top_5 = sorted_all[:5]
        remaining = sorted_all[5:]

        print(f" Top 5 articles: {len(top_5)}")
        print(f" Remaining articles: {len(remaining)}")

        print(f"\n Top 5 Articles (by rank_score):")
        for article in top_5:
            headline = self._get_headline(article)
            score = article.get("rank_score", 0.0)
            print(
                f"   [{article.get('id','?')}] {headline[:60]}... (score: {score:.2f})"
            )

        return top_5, remaining

    def generate_summary(self, articles: List[Dict]) -> str:
        """
        Generate comprehensive summary from top 5 articles using Groq API.

        Args:
            articles: List of top 5 articles to summarize

        Returns:
            Combined summary string
        """
        try:
            article_contents = []
            for i, article in enumerate(articles[:5], 1):
                headline = self._get_headline(article)
                text = self._get_text(article)
                source = article.get("source", "Unknown")

                article_content = f"Article {i} ({source}):\nHeadline: {headline}\nContent: {text[:1000]}..."
                article_contents.append(article_content)

            combined_content = "\n\n".join(article_contents)

            prompt = f"""Please create a comprehensive summary of the following top 5 news articles. Focus on the key themes, important developments, and main points that connect these articles. 
            The summary should be concise but capture the essential information that would be useful for finding similar articles.
            {combined_content}
            Please provide a summary in 3-4 sentences that captures the main themes and key information from these articles."""

            # Call Groq API
            response = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="openai/gpt-oss-20b",
                temperature=0.3,
                max_completion_tokens=8192,
                top_p=1,
                reasoning_effort="medium",
                stream=False,
                stop=None,
                tools=[{"type": "browser_search"}],
            )

            summary = response.choices[0].message.content.strip()
            print(f"   Generated Groq summary: \n{summary}")
            return summary

        except Exception as e:
            print(f"   Error generating Groq summary: {e}")
            return None

    def compute_similarities(
        self, top_articles: List[Dict], remaining_articles: List[Dict]
    ) -> List[Dict]:
        """
        Compute similarity scores and select articles.

        Args:
            top_articles: Top 5 articles from ranking
            remaining_articles: Remaining articles to compare

        Returns:
            List of selected articles with similarity scores
        """
        print(f"\n Starting similarity computation...")

        print(
            f"\n Step 1: Generating comprehensive summary for top {len(top_articles)} articles using Groq API..."
        )
        combined_summary = self.generate_summary(top_articles)
        print(f"\n Combined summary length: {len(combined_summary)} characters")

        print(f"\n Step 2: Encoding texts with Sentence Transformer...")
        summary_embedding = self.model.encode(combined_summary, convert_to_tensor=True)

        remaining_texts = [self._get_text(art) for art in remaining_articles]
        remaining_embeddings = self.model.encode(
            remaining_texts, convert_to_tensor=True
        )
        print(f" Encoded {len(remaining_articles)} article embeddings")

        print(f"\n Step 3: Computing cosine similarity scores...")
        similarities = util.cos_sim(summary_embedding, remaining_embeddings)[0]

        for idx, article in enumerate(remaining_articles):
            article["similarity_score"] = float(similarities[idx])

        sorted_articles = sorted(
            remaining_articles, key=lambda x: x["similarity_score"], reverse=True
        )

        print(f" Similarity scores computed")
        print(f"\n Top 10 similarity scores:")
        for i, art in enumerate(sorted_articles[:10]):
            print(
                f"   {i+1}. Article {art.get('id','?')}: {art.get('similarity_score',0.0):.4f}"
            )

        print(f"\n Step 4: Selecting articles...")
        print(
            f"   Target: Top {self.top_k} + any above {self.similarity_threshold} threshold"
        )

        selected = sorted_articles[: self.top_k]
        selected_ids = {art.get("id") for art in selected}

        additional = []
        for article in sorted_articles[self.top_k :]:
            if article.get("similarity_score", 0.0) > self.similarity_threshold:
                additional.append(article)
                selected_ids.add(article.get("id"))
                print(
                    f"     Added article {article.get('id','?')} (score: {article.get('similarity_score',0.0):.4f})"
                )

        selected.extend(additional)

        print(f"\n Selected {len(selected)} articles:")
        print(
            f"   - Top {min(self.top_k, len(sorted_articles))}: {min(self.top_k, len(sorted_articles))} articles"
        )
        print(f"   - Above threshold: {len(additional)} articles")

        return selected

    def combine_and_save(
        self, top_articles: List[Dict], selected_articles: List[Dict], output_file: str
    ):
        """
        Combine top 5 and selected articles, save to JSON.

        Args:
            top_articles: Top 5 articles
            selected_articles: Selected similar articles
            output_file: Output JSON file path
        """
        print(f"\n Combining and saving results...")

        final_articles = top_articles + selected_articles

        seen_ids = set()
        unique_articles = []
        for article in final_articles:
            art_id = article.get("id")
            if art_id not in seen_ids:
                unique_articles.append(article)
                seen_ids.add(art_id)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(unique_articles, f, indent=2, ensure_ascii=False)

        print(f" Saved {len(unique_articles)} articles to {output_file}")
        print(f"\n Final composition:")
        print(f"   - Top 5 (with rank_score): {len(top_articles)}")
        print(f"   - Selected similar articles: {len(selected_articles)}")
        print(f"   - Total: {len(unique_articles)}")

        return unique_articles

    def run(self, input_file: str, output_file: str = "output.json") -> List[Dict]:
        """
        Run the complete pipeline.

        Args:
            input_file: Path to input JSON file
            output_file: Path to output JSON file

        Returns:
            List of final articles
        """
        print("=" * 70)
        print("SIMILARITY-BASED EXPANSION PIPELINE")
        print("=" * 70)

        articles = self.load_input(input_file)

        top_5, remaining = self.separate_articles(articles)

        if len(top_5) == 0:
            raise ValueError("No articles found with usable 'rank_score'!")

        if len(remaining) == 0:
            print(
                "\n No remaining articles after top 5. Skipping similarity step and saving top 5 only."
            )
            final_articles = self.combine_and_save(top_5, [], output_file)
            print("\n" + "=" * 70)
            print(" PIPELINE COMPLETE")
            print("=" * 70)
            return final_articles

        selected = self.compute_similarities(top_5, remaining)

        final_articles = self.combine_and_save(top_5, selected, output_file)

        print("\n" + "=" * 70)
        print(" PIPELINE COMPLETE")
        print("=" * 70)

        return final_articles
