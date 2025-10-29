import json
import numpy as np
from sentence_transformers import SentenceTransformer, util
from typing import List, Dict, Tuple
from pathlib import Path

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

    def __init__(self, 
                 model_name: str = 'all-MiniLM-L6-v2',
                 similarity_threshold: float = 0.5,
                 top_k: int = 10):
        """
        Initialize the pipeline.

        Args:
            model_name: Sentence transformer model to use
            similarity_threshold: Minimum similarity score for inclusion
            top_k: Number of top similar articles to select
        """
        print(f" Initializing Similarity Expansion Pipeline...")
        self.model = SentenceTransformer(model_name)
        self.similarity_threshold = similarity_threshold
        self.top_k = top_k
        print(f" Loaded model: {model_name}")
        print(f"   Similarity threshold: {similarity_threshold}")
        print(f"   Top-K: {top_k}")

    def load_input(self, input_file: str) -> List[Dict]:
        """Load articles from JSON file."""
        print(f"\n Loading input file: {input_file}")
        with open(input_file, 'r', encoding='utf-8') as f:
            articles = json.load(f)
        print(f" Loaded {len(articles)} articles")
        return articles

    def separate_articles(self, articles: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        Separate articles into top 5 (with rank_score) and remaining.

        Args:
            articles: List of all articles

        Returns:
            Tuple of (top_5_articles, remaining_articles)
        """
        print(f"\n Separating articles by rank_score field...")

        top_5 = []
        remaining = []

        for article in articles:
            if 'rank_score' in article:
                top_5.append(article)
            else:
                remaining.append(article)

        # Sort top 5 by rank_score (descending)
        top_5.sort(key=lambda x: x.get('rank_score', 0), reverse=True)

        print(f" Top 5 articles: {len(top_5)}")
        print(f" Remaining articles: {len(remaining)}")

        # Print top 5 for verification
        print(f"\n Top 5 Articles (by rank_score):")
        for article in top_5:
            print(f"   [{article['id']}] {article['title'][:60]}... (score: {article['rank_score']:.2f})")

        return top_5, remaining

    def generate_summary(self, text: str, num_sentences: int = 3) -> str:
        """
        Generate extractive summary from text.

        Args:
            text: Article content
            num_sentences: Number of sentences to extract

        Returns:
            Summary string
        """
        sentences = text.split('.')
        summary = '. '.join(sentences[:num_sentences]).strip()
        if not summary.endswith('.'):
            summary += '.'
        return summary

    def compute_similarities(self, 
                            top_articles: List[Dict], 
                            remaining_articles: List[Dict]) -> List[Dict]:
        """
        Compute similarity scores and select articles.

        Args:
            top_articles: Top 5 articles from ranking
            remaining_articles: Remaining articles to compare

        Returns:
            List of selected articles with similarity scores
        """
        print(f"\n Starting similarity computation...")

        # Step 1: Generate summaries of top 5
        print(f"\n Step 1: Generating summaries for top {len(top_articles)} articles...")
        summaries = []
        for article in top_articles:
            summary = self.generate_summary(article['content'])
            summaries.append(summary)
            print(f"   Article {article['id']}: {summary[:70]}...")

        # Combine all summaries
        combined_summary = ' '.join(summaries)
        print(f"\n Combined summary length: {len(combined_summary)} characters")

        # Step 2: Encode texts
        print(f"\n Step 2: Encoding texts with Sentence Transformer...")
        summary_embedding = self.model.encode(combined_summary, convert_to_tensor=True)

        remaining_texts = [art['content'] for art in remaining_articles]
        remaining_embeddings = self.model.encode(remaining_texts, convert_to_tensor=True)
        print(f" Encoded {len(remaining_articles)} article embeddings")

        # Step 3: Compute cosine similarities
        print(f"\n Step 3: Computing cosine similarity scores...")
        similarities = util.cos_sim(summary_embedding, remaining_embeddings)[0]

        # Add similarity scores to articles
        for idx, article in enumerate(remaining_articles):
            article['similarity_score'] = float(similarities[idx])

        # Sort by similarity (descending)
        sorted_articles = sorted(
            remaining_articles,
            key=lambda x: x['similarity_score'],
            reverse=True
        )

        print(f" Similarity scores computed")
        print(f"\n Top 10 similarity scores:")
        for i, art in enumerate(sorted_articles[:10]):
            print(f"   {i+1}. Article {art['id']}: {art['similarity_score']:.4f}")

        # Step 4: Select articles
        print(f"\n Step 4: Selecting articles...")
        print(f"   Target: Top {self.top_k} + any above {self.similarity_threshold} threshold")

        # Select top K
        selected = sorted_articles[:self.top_k]
        selected_ids = {art['id'] for art in selected}

        # Add any additional articles above threshold
        additional = []
        for article in sorted_articles[self.top_k:]:
            if article['similarity_score'] > self.similarity_threshold:
                additional.append(article)
                selected_ids.add(article['id'])
                print(f"     Added article {article['id']} (score: {article['similarity_score']:.4f})")

        selected.extend(additional)

        print(f"\n Selected {len(selected)} articles:")
        print(f"   - Top {min(self.top_k, len(sorted_articles))}: {min(self.top_k, len(sorted_articles))} articles")
        print(f"   - Above threshold: {len(additional)} articles")

        return selected

    def combine_and_save(self, 
                        top_articles: List[Dict], 
                        selected_articles: List[Dict],
                        output_file: str):
        """
        Combine top 5 and selected articles, save to JSON.

        Args:
            top_articles: Top 5 articles
            selected_articles: Selected similar articles
            output_file: Output JSON file path
        """
        print(f"\n Combining and saving results...")

        # Combine all articles
        final_articles = top_articles + selected_articles

        seen_ids = set()
        unique_articles = []
        for article in final_articles:
            if article['id'] not in seen_ids:
                unique_articles.append(article)
                seen_ids.add(article['id'])

        # Save to JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(unique_articles, f, indent=2, ensure_ascii=False)

        print(f" Saved {len(unique_articles)} articles to {output_file}")
        print(f"\n Final composition:")
        print(f"   - Top 5 (with rank_score): {len(top_articles)}")
        print(f"   - Selected similar articles: {len(selected_articles)}")
        print(f"   - Total: {len(unique_articles)}")

        return unique_articles

    def run(self, input_file: str, output_file: str = 'output.json') -> List[Dict]:
        """
        Run the complete pipeline.

        Args:
            input_file: Path to input JSON file
            output_file: Path to output JSON file

        Returns:
            List of final articles
        """
        print("="*70)
        print("SIMILARITY-BASED EXPANSION PIPELINE")
        print("="*70)

        # Load input
        articles = self.load_input(input_file)

        # Separate articles
        top_5, remaining = self.separate_articles(articles)

        if len(top_5) == 0:
            raise ValueError("No articles with 'rank_score' field found!")

        if len(remaining) == 0:
            raise ValueError("No remaining articles found for similarity comparison!")

        # Compute similarities and select
        selected = self.compute_similarities(top_5, remaining)

        # Combine and save
        final_articles = self.combine_and_save(top_5, selected, output_file)

        print("\n" + "="*70)
        print(" PIPELINE COMPLETE")
        print("="*70)

        return final_articles

    def visualize_results(self, final_articles: List[Dict]):
        """
        Print detailed visualization of results.

        Args:
            final_articles: List of final selected articles
        """
        print("\n" + "="*70)
        print("DETAILED RESULTS")
        print("="*70)

        # Separate by type
        top_5 = [art for art in final_articles if 'rank_score' in art]
        selected = [art for art in final_articles if 'rank_score' not in art]

        print(f"\n TOP 5 ARTICLES (from rule-based ranking):")
        for article in sorted(top_5, key=lambda x: x['rank_score'], reverse=True):
            print(f"\n   [{article['id']}] {article['title']}")
            print(f"       Rank Score: {article['rank_score']:.2f}")
            print(f"       Date: {article['date']}")
            print(f"       Impact: {article.get('impact_level', 'N/A')}")

        print(f"\n\n SELECTED {len(selected)} SIMILAR ARTICLES:")
        for article in sorted(selected, key=lambda x: x.get('similarity_score', 0), reverse=True):
            print(f"\n   [{article['id']}] {article['title']}")
            print(f"       Similarity: {article.get('similarity_score', 0):.4f}")
            print(f"       Date: {article['date']}")
            print(f"       Impact: {article.get('impact_level', 'N/A')}")

        print("\n" + "="*70)