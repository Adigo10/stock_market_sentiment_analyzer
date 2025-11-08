import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { TrendingUp, Download, AlertCircle } from 'lucide-react';
import { apiService } from '@/services/api';
import { Button } from './Button';
import { Card } from './Card';
import { LoadingSpinner, ProgressBar } from './LoadingSpinner';
import { MetricCard } from './MetricCard';
import { StepCard } from './StepCard';
import { DataTable } from './DataTable';
import { ArticleCard } from './ArticleCard';
import { ThemeToggle } from './ThemeToggle';
import type { Article, SentimentStats, KeyphraseCounter } from '@/types';
import { parseSentiment, formatTableDate, truncateText, downloadJSON, getSafeCompanyName, normalizeSentimentType } from '@/utils/helpers';

type AnalysisStatus = 'idle' | 'step1' | 'step2' | 'step3' | 'completed' | 'error';

export const Dashboard: React.FC = () => {
  const [companies, setCompanies] = useState<string[]>([]);
  const [selectedCompany, setSelectedCompany] = useState<string>('');
  const [status, setStatus] = useState<AnalysisStatus>('idle');
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState('');
  const [error, setError] = useState<string | null>(null);

  // Step data
  const [rankedArticles, setRankedArticles] = useState<Article[]>([]);
  const [enrichedArticles, setEnrichedArticles] = useState<Article[]>([]);
  const [sentimentStats, setSentimentStats] = useState<SentimentStats | null>(null);
  const [aggregatedKeyphrases, setAggregatedKeyphrases] = useState<{
    positive: [string, number][];
    negative: [string, number][];
    neutral: [string, number][];
  } | null>(null);

  useEffect(() => {
    loadCompanies();
  }, []);

  const loadCompanies = async () => {
    try {
      const companiesList = await apiService.getCompanies();
      setCompanies(companiesList);
      if (companiesList.length > 0) {
        setSelectedCompany(companiesList[0]);
      }
    } catch (err) {
      console.error('Failed to load companies:', err);
      setError('Unable to connect to the backend server. Please ensure it is running.');
    }
  };

  const aggregateKeyphrases = (articles: Article[]) => {
    const positive: KeyphraseCounter = {};
    const negative: KeyphraseCounter = {};
    const neutral: KeyphraseCounter = {};

    articles.forEach((article) => {
      const kp = article.keyphrase_analysis?.keyphrases;
      if (!kp) return;

      kp.positive?.forEach((item) => {
        positive[item.phrase] = (positive[item.phrase] || 0) + item.confidence;
      });
      kp.negative?.forEach((item) => {
        negative[item.phrase] = (negative[item.phrase] || 0) + item.confidence;
      });
      kp.neutral?.forEach((item) => {
        neutral[item.phrase] = (neutral[item.phrase] || 0) + item.confidence;
      });
    });

    const sortByValue = (obj: KeyphraseCounter): [string, number][] =>
      Object.entries(obj).sort((a, b) => b[1] - a[1]).slice(0, 10);

    return {
      positive: sortByValue(positive),
      negative: sortByValue(negative),
      neutral: sortByValue(neutral),
    };
  };

  const handleAnalyze = async () => {
    if (!selectedCompany) return;

    setStatus('step1');
    setProgress(5);
    setError(null);
    setRankedArticles([]);
    setEnrichedArticles([]);
    setSentimentStats(null);
    setAggregatedKeyphrases(null);

    try {
      // Step 1: Fetch and Rank
      setStatusMessage('Fetching and ranking latest financial news...');
      const fetchResponse = await apiService.fetchAndRank(selectedCompany);
      setRankedArticles(fetchResponse.articles);
      setProgress(25);

      // Step 2: Enrich with AI
      setStatus('step2');
      setProgress(45);
      setStatusMessage('Running AI sentiment analysis and similarity expansion...');
      const enrichResponse = await apiService.enrichWithAI(selectedCompany);
      setEnrichedArticles(enrichResponse.articles);
      setSentimentStats(enrichResponse.sentiment_stats);
      setProgress(75);

      // Step 3: Aggregate keyphrases
      setStatus('step3');
      setProgress(90);
      setStatusMessage('Aggregating keyphrases and generating intelligence report...');
      const aggregated = aggregateKeyphrases(enrichResponse.articles);
      setAggregatedKeyphrases(aggregated);
      setProgress(100);

      setStatus('completed');
      setStatusMessage('Analysis completed successfully!');
    } catch (err: any) {
      console.error('Analysis error:', err);
      setStatus('error');
      setError(err.response?.data?.message || err.message || 'An unexpected error occurred');
      setProgress(0);
    }
  };

  const handleDownload = () => {
    if (enrichedArticles.length === 0) return;
    const filename = `${getSafeCompanyName(selectedCompany)}_ai_articles.json`;
    downloadJSON(enrichedArticles, filename);
  };

  const getStepStatus = (step: number): 'pending' | 'loading' | 'completed' | 'error' => {
    if (status === 'error') return step <= getCompletedStep() ? 'error' : 'pending';
    if (step < getCompletedStep()) return 'completed';
    if (step === getCompletedStep()) return 'loading';
    return 'pending';
  };

  const getCompletedStep = (): number => {
    switch (status) {
      case 'step1': return 1;
      case 'step2': return 2;
      case 'step3': return 3;
      case 'completed': return 4;
      default: return 0;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <TrendingUp className="text-blue-600 dark:text-blue-400" size={32} />
              <div>
                <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
                  AI Stock Market Sentiment Analyzer
                </h1>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Powered by Flan-T5 AI Model • Real-time News Analysis • Keyphrase Extraction
                </p>
              </div>
            </div>
            <ThemeToggle />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && !companies.length ? (
          <Card className="p-6">
            <div className="flex items-start gap-4">
              <AlertCircle className="text-red-500 flex-shrink-0" size={24} />
              <div>
                <h3 className="text-lg font-semibold text-red-800 dark:text-red-400 mb-2">
                  Connection Error
                </h3>
                <p className="text-gray-700 dark:text-gray-300 mb-4">{error}</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Make sure the backend server is running at <code className="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">http://localhost:8000</code>
                </p>
              </div>
            </div>
          </Card>
        ) : (
          <>
            {/* Company Selection */}
            <Card className="p-6 mb-8">
              <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                Select Company to Analyze
              </label>
              <div className="flex gap-4 items-center">
                <select
                  value={selectedCompany}
                  onChange={(e) => setSelectedCompany(e.target.value)}
                  disabled={status !== 'idle' && status !== 'completed' && status !== 'error'}
                  className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {companies.map((company) => (
                    <option key={company} value={company}>
                      {company}
                    </option>
                  ))}
                </select>
                <Button
                  onClick={handleAnalyze}
                  disabled={!selectedCompany || (status !== 'idle' && status !== 'completed' && status !== 'error')}
                  isLoading={status !== 'idle' && status !== 'completed' && status !== 'error'}
                  size="lg"
                  className="px-8 whitespace-nowrap"
                >
                  {status !== 'idle' && status !== 'completed' && status !== 'error' ? 'Analyzing...' : '🚀 Analyze with AI'}
                </Button>
              </div>
            </Card>

            {/* Progress Bar */}
            {status !== 'idle' && status !== 'completed' && (
              <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-8"
              >
                <Card className="p-6">
                  <ProgressBar progress={progress} label={statusMessage} />
                </Card>
              </motion.div>
            )}

            {/* Error Message */}
            {status === 'error' && error && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="mb-8"
              >
                <Card className="p-6 border-l-4 border-red-500">
                  <div className="flex items-start gap-4">
                    <AlertCircle className="text-red-500 flex-shrink-0" size={24} />
                    <div>
                      <h3 className="text-lg font-semibold text-red-800 dark:text-red-400 mb-2">
                        Analysis Failed
                      </h3>
                      <p className="text-gray-700 dark:text-gray-300">{error}</p>
                    </div>
                  </div>
                </Card>
              </motion.div>
            )}

            {/* Analysis Steps */}
            <AnimatePresence mode="wait">
              {(status !== 'idle' || rankedArticles.length > 0) && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="space-y-6"
                >
                  {/* Step 1: Fetch & Rank */}
                  {rankedArticles.length > 0 && (
                    <StepCard
                      stepNumber={1}
                      title="Fetch & Rank"
                      status={getStepStatus(1)}
                      expandable={true}
                      summary={
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                          <MetricCard
                            label="Articles Retrieved"
                            value={rankedArticles.length}
                            icon="📰"
                            delay={0}
                          />
                          <MetricCard
                            label="Pipeline Status"
                            value="SUCCESS"
                            icon="✅"
                            delay={0.1}
                          />
                          <MetricCard
                            label="Latest Article"
                            value={formatTableDate(rankedArticles[0])}
                            icon="📅"
                            delay={0.2}
                          />
                          <MetricCard
                            label="Top Rank Score"
                            value={rankedArticles[0]?.rank_score?.toFixed(3) || '0.000'}
                            icon="⭐"
                            delay={0.3}
                          />
                        </div>
                      }
                      details={
                        <DataTable
                          columns={[
                            { key: 'headline', label: 'Headline', render: (val) => truncateText(val, 60) },
                            { key: 'source', label: 'Source' },
                            { key: 'rank_score', label: 'Rank Score', render: (val) => val.toFixed(3) },
                            { key: 'publish_date', label: 'Date' },
                          ]}
                          data={rankedArticles.slice(0, 15).map((art) => ({
                            headline: art.headline || art.title || 'Unknown',
                            source: art.source || 'Unknown',
                            rank_score: art.rank_score || 0,
                            publish_date: formatTableDate(art),
                          }))}
                        />
                      }
                    />
                  )}

                  {/* Step 2: AI Sentiment Analysis */}
                  {enrichedArticles.length > 0 && sentimentStats && (
                    <StepCard
                      stepNumber={2}
                      title="AI Sentiment Synthesis"
                      status={getStepStatus(2)}
                      expandable={true}
                      summary={
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                          <MetricCard
                            label="Positive"
                            value={sentimentStats.positive}
                            icon="🟢"
                            delay={0}
                          />
                          <MetricCard
                            label="Negative"
                            value={sentimentStats.negative}
                            icon="🔴"
                            delay={0.1}
                          />
                          <MetricCard
                            label="Neutral"
                            value={sentimentStats.neutral}
                            icon="⚪"
                            delay={0.2}
                          />
                          <MetricCard
                            label="Keyphrases"
                            value={sentimentStats.total_keyphrases}
                            icon="🔑"
                            delay={0.3}
                          />
                        </div>
                      }
                      details={
                        <DataTable
                          columns={[
                            { key: 'rank', label: 'Rank' },
                            { key: 'sentiment', label: 'Sentiment' },
                            { key: 'headline', label: 'Headline', render: (val) => truncateText(val, 50) },
                            { key: 'reason', label: 'Reason', render: (val) => truncateText(val, 60) },
                          ]}
                          data={enrichedArticles.slice(0, 15).map((art, idx) => {
                            const rawSentiment = art.predicted_sentiment || '';
                            const { type, reason } = parseSentiment(rawSentiment);
                            
                            // Debug: log the first few to see what we're getting
                            if (idx < 3) {
                              console.log(`Article ${idx + 1}:`, {
                                raw: rawSentiment,
                                parsed_type: type,
                                parsed_reason: reason
                              });
                            }
                            
                            // Normalize the type to ensure consistent display
                            let displaySentiment = 'Neutral';
                            if (type === 'positive' || type === 'good') {
                              displaySentiment = 'Positive';
                            } else if (type === 'negative' || type === 'bad') {
                              displaySentiment = 'Negative';
                            } else if (type === 'neutral') {
                              displaySentiment = 'Neutral';
                            }
                            
                            return {
                              rank: idx + 1,
                              sentiment: displaySentiment,
                              headline: art.headline || art.title || 'Unknown',
                              reason: `Sentiment: ${displaySentiment}. Reason: ${reason}`,
                            };
                          })}
                        />
                      }
                    />
                  )}

                  {/* Step 3: Keyphrase Intelligence */}
                  {aggregatedKeyphrases && (
                    <StepCard
                      stepNumber={3}
                      title="Keyphrase Intelligence"
                      status={getStepStatus(3)}
                      expandable={false}
                      details={
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {/* Bullish Signals */}
                        {aggregatedKeyphrases.positive.length > 0 && (
                          <div>
                            <h4 className="text-lg font-bold text-green-700 dark:text-green-400 mb-4 flex items-center gap-2">
                              <span>🟢</span>
                              <span>Bullish Signals</span>
                            </h4>
                            <DataTable
                              columns={[
                                { key: 'phrase', label: 'Phrase' },
                                { key: 'confidence', label: 'Confidence', render: (val) => val.toFixed(4) },
                              ]}
                              data={aggregatedKeyphrases.positive.map(([phrase, confidence]) => ({
                                phrase,
                                confidence,
                              }))}
                            />
                          </div>
                        )}

                        {/* Bearish Signals */}
                        {aggregatedKeyphrases.negative.length > 0 && (
                          <div>
                            <h4 className="text-lg font-bold text-red-700 dark:text-red-400 mb-4 flex items-center gap-2">
                              <span>🔴</span>
                              <span>Bearish Signals</span>
                            </h4>
                            <DataTable
                              columns={[
                                { key: 'phrase', label: 'Phrase' },
                                { key: 'confidence', label: 'Confidence', render: (val) => val.toFixed(4) },
                              ]}
                              data={aggregatedKeyphrases.negative.map(([phrase, confidence]) => ({
                                phrase,
                                confidence,
                              }))}
                            />
                          </div>
                        )}

                        {/* Neutral Themes */}
                        {aggregatedKeyphrases.neutral.length > 0 && (
                          <div>
                            <h4 className="text-lg font-bold text-gray-700 dark:text-gray-400 mb-4 flex items-center gap-2">
                              <span>⚪</span>
                              <span>Neutral Themes</span>
                            </h4>
                            <DataTable
                              columns={[
                                { key: 'phrase', label: 'Phrase' },
                                { key: 'confidence', label: 'Confidence', render: (val) => val.toFixed(4) },
                              ]}
                              data={aggregatedKeyphrases.neutral.map(([phrase, confidence]) => ({
                                phrase,
                                confidence,
                              }))}
                            />
                          </div>
                        )}
                      </div>
                      }
                    />
                  )}

                  {/* AI-Enriched Articles */}
                  {status === 'completed' && enrichedArticles.length > 0 && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.3 }}
                    >
                      <Card className="p-6">
                        <div className="flex items-center justify-between mb-6">
                          <div>
                            <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                              📰 AI-Enriched Articles
                            </h2>
                            <p className="text-gray-600 dark:text-gray-400">
                              Showing {Math.min(enrichedArticles.length, 15)} of {enrichedArticles.length} analyzed articles
                            </p>
                          </div>
                          <Button onClick={handleDownload} variant="outline" className="gap-2">
                            <Download size={18} />
                            Download JSON
                          </Button>
                        </div>

                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                          {enrichedArticles.slice(0, 15).map((article, idx) => (
                            <ArticleCard key={idx} article={article} index={idx} />
                          ))}
                        </div>
                      </Card>
                    </motion.div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </>
        )}
      </main>
    </div>
  );
};

