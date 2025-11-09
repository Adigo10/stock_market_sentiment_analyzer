export interface Article {
  headline?: string;
  title?: string;
  summary?: string;
  content?: string;
  url?: string;
  source?: string;
  publish_date?: string;
  published_date?: string;
  date?: string;
  datetime?: string;
  rank_score?: number;
  predicted_sentiment?: string;
  keyphrase_analysis?: KeyphraseAnalysis;
}

export interface KeyphraseAnalysis {
  keyphrases: {
    positive: KeyphraseItem[];
    negative: KeyphraseItem[];
    neutral: KeyphraseItem[];
  };
}

export interface KeyphraseItem {
  phrase: string;
  confidence: number;
}

export interface SentimentStats {
  positive: number;
  negative: number;
  neutral: number;
  total_keyphrases: number;
}

export interface Top5Article {
  id: string | number;
  headline: string;
  rank_score: number;
  source: string;
  date: string;
}

export interface SimilarityScore {
  id: string | number;
  headline: string;
  score: number;
  source: string;
}

export interface PipelineMetrics {
  timings: {
    load?: number;
    separation?: number;
    summary_generation?: number;
    summary_encoding?: number;
    text_preparation?: number;
    articles_encoding?: number;
    total_encoding?: number;
    score_assignment?: number;
    sorting?: number;
    similarity_computation?: number;
    selection?: number;
    total_computation?: number;
    save?: number;
    total?: number;
  };
  stats: {
    input_articles?: number;
    top_articles?: number;
    remaining_articles?: number;
    selected_similar?: number;
    final_articles?: number;
    articles_per_second?: number;
  };
  details: {
    top_5?: Top5Article[];
    groq_summary?: string;
    top_10_scores?: SimilarityScore[];
    additional_articles?: Array<{
      id: string | number;
      headline: string;
      score: number;
    }>;
    selection_count?: {
      top_k: number;
      above_threshold: number;
      total_selected: number;
    };
    model_name?: number;
    threshold?: number;
    top_k?: number;
  };
}

export interface FetchRankResponse {
  status: string;
  articles: Article[];
  message?: string;
  pipeline_metrics?: PipelineMetrics;
}

export interface EnrichResponse {
  status: string;
  articles: Article[];
  sentiment_stats: SentimentStats;
  message?: string;
}

export interface CompaniesResponse {
  companies: string[];
}

export type SentimentType = 'positive' | 'negative' | 'neutral' | 'good' | 'bad';

export interface ParsedSentiment {
  type: SentimentType;
  reason: string;
}

export interface KeyphraseCounter {
  [phrase: string]: number;
}

export interface AnalysisStep {
  step: number;
  title: string;
  status: 'pending' | 'loading' | 'completed' | 'error';
  data?: any;
}

