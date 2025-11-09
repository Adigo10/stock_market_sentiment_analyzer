import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ExternalLink, Calendar, Star, ChevronDown, ChevronUp } from 'lucide-react';
import { Card } from './Card';
import { SentimentBadge, KeyphraseBadge } from './Badge';
import type { Article } from '@/types';
import { parseSentiment, formatArticleDate, truncateText, formatHeadline, cleanText } from '@/utils/helpers';

interface ArticleCardProps {
  article: Article;
  index: number;
}

export const ArticleCard: React.FC<ArticleCardProps> = ({ article, index }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  const rawHeadline = article.headline || article.title || 'No headline';
  const headline = formatHeadline(rawHeadline);
  const rawSummary = article.summary || article.content || 'No summary available';
  const summary = cleanText(rawSummary);
  const url = article.url || '#';
  const rankScore = article.rank_score || 0;
  
  const { type: sentimentType, reason: sentimentReason } = parseSentiment(
    article.predicted_sentiment || ''
  );
  
  const keyphrases = article.keyphrase_analysis?.keyphrases;
  const formattedDate = formatArticleDate(article);

  const shouldTruncate = summary.length > 320;
  const displaySummary = shouldTruncate && !isExpanded ? truncateText(summary, 320) : summary;

  return (
    <Card animate delay={index * 0.05} className="p-6 hover:shadow-lg transition-shadow duration-300">
      <div className="flex flex-col gap-4">
        {/* Header */}
        <div className="flex items-start justify-between gap-4">
          <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 flex-1">
            <span className="text-gray-900 dark:text-gray-100">{index + 1}.</span> {headline}
          </h3>
          <SentimentBadge sentiment={sentimentType} />
        </div>

        {/* Metadata */}
        <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
          <div className="flex items-center gap-1">
            <Calendar size={16} />
            <span>{formattedDate}</span>
          </div>
          <div className="flex items-center gap-1">
            <Star size={16} className="text-yellow-500" />
            <span>Rank: {rankScore.toFixed(3)}</span>
          </div>
        </div>

        {/* Summary */}
        <div>
          <p className="text-gray-700 dark:text-gray-300 leading-relaxed text-justify">
            {displaySummary}
          </p>
          
          {/* Expand/Collapse Button */}
          {shouldTruncate && (
            <motion.button
              onClick={() => setIsExpanded(!isExpanded)}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="mt-3 flex items-center gap-2 text-blue-600 dark:text-blue-400 font-semibold hover:underline"
            >
              {isExpanded ? (
                <>
                  <ChevronUp size={20} />
                  <span>Show Less</span>
                </>
              ) : (
                <>
                  <ChevronDown size={20} />
                  <span>Show More</span>
                </>
              )}
            </motion.button>
          )}
        </div>

        {/* AI Sentiment Analysis */}
        {sentimentReason && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            transition={{ duration: 0.3, delay: 0.2 }}
            className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4"
          >
            <div className="flex items-center gap-2 font-semibold text-blue-900 dark:text-blue-300 mb-2">
              <span>🤖</span>
              <span>AI Sentiment Analysis</span>
            </div>
            <p className="text-sm text-gray-700 dark:text-gray-300">
              {truncateText(cleanText(sentimentReason), 240)}
            </p>
          </motion.div>
        )}

        {/* Keyphrases */}
        {keyphrases && (keyphrases.positive?.length || keyphrases.negative?.length || keyphrases.neutral?.length) ? (
          <div>
            <div className="font-semibold text-gray-900 dark:text-gray-100 mb-2 flex items-center gap-2">
              <span>🔑</span>
              <span>Key Phrases</span>
            </div>
            <div className="flex flex-wrap -m-1">
              {keyphrases.positive?.slice(0, 8).map((kp, idx) => (
                <KeyphraseBadge key={idx} phrase={kp.phrase} confidence={kp.confidence} type="positive" />
              ))}
              {keyphrases.negative?.slice(0, 8).map((kp, idx) => (
                <KeyphraseBadge key={idx} phrase={kp.phrase} confidence={kp.confidence} type="negative" />
              ))}
              {keyphrases.neutral?.slice(0, 8).map((kp, idx) => (
                <KeyphraseBadge key={idx} phrase={kp.phrase} confidence={kp.confidence} type="neutral" />
              ))}
            </div>
          </div>
        ) : null}

        {/* Read More Link */}
        {url && url !== '#' && (
          <motion.a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="inline-flex items-center gap-2 text-blue-600 dark:text-blue-400 font-semibold hover:underline mt-2"
          >
            <ExternalLink size={16} />
            <span>Read Full Article</span>
          </motion.a>
        )}
      </div>
    </Card>
  );
};

