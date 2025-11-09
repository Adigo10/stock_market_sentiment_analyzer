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

export interface FetchRankResponse {
  status: string;
  articles: Article[];
  message?: string;
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

