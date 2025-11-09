import React from 'react';
import { motion } from 'framer-motion';
import { Clock, Database, Sparkles, TrendingUp, CheckCircle, Cpu } from 'lucide-react';
import type { PipelineMetrics } from '@/types';

interface PipelineDetailsProps {
  metrics: PipelineMetrics;
}

export const PipelineDetails: React.FC<PipelineDetailsProps> = ({ metrics }) => {
  const { timings, stats, details } = metrics;

  // Calculate percentages for timing chart
  const totalTime = timings.total || 1;
  const timingBreakdown = [
    { name: 'Load & Separation', time: (timings.load || 0) + (timings.separation || 0), color: 'bg-blue-500' },
    { name: 'Summary Generation', time: timings.summary_generation || 0, color: 'bg-purple-500' },
    { name: 'Text Encoding', time: timings.total_encoding || 0, color: 'bg-green-500' },
    { name: 'Similarity Computation', time: timings.similarity_computation || 0, color: 'bg-yellow-500' },
    { name: 'Save', time: timings.save || 0, color: 'bg-pink-500' },
  ].filter(item => item.time > 0);

  return (
    <div className="space-y-6">
      {/* Overview Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 p-4 rounded-lg border border-blue-200 dark:border-blue-700"
        >
          <div className="flex items-center gap-2 mb-2">
            <Database size={20} className="text-blue-600 dark:text-blue-400" />
            <span className="text-sm font-semibold text-blue-900 dark:text-blue-300">Input Articles</span>
          </div>
          <p className="text-2xl font-bold text-blue-700 dark:text-blue-400">{stats.input_articles || 0}</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 p-4 rounded-lg border border-green-200 dark:border-green-700"
        >
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle size={20} className="text-green-600 dark:text-green-400" />
            <span className="text-sm font-semibold text-green-900 dark:text-green-300">Selected</span>
          </div>
          <p className="text-2xl font-bold text-green-700 dark:text-green-400">{stats.final_articles || 0}</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 p-4 rounded-lg border border-purple-200 dark:border-purple-700"
        >
          <div className="flex items-center gap-2 mb-2">
            <Clock size={20} className="text-purple-600 dark:text-purple-400" />
            <span className="text-sm font-semibold text-purple-900 dark:text-purple-300">Total Time</span>
          </div>
          <p className="text-2xl font-bold text-purple-700 dark:text-purple-400">{(timings.total || 0).toFixed(2)}s</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20 p-4 rounded-lg border border-orange-200 dark:border-orange-700"
        >
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp size={20} className="text-orange-600 dark:text-orange-400" />
            <span className="text-sm font-semibold text-orange-900 dark:text-orange-300">Speed</span>
          </div>
          <p className="text-2xl font-bold text-orange-700 dark:text-orange-400">{(stats.articles_per_second || 0).toFixed(1)}/s</p>
        </motion.div>
      </div>

      {/* Timing Breakdown Chart */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700"
      >
        <div className="flex items-center gap-2 mb-4">
          <Clock className="text-blue-600 dark:text-blue-400" size={24} />
          <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">Pipeline Timing Breakdown</h3>
        </div>
        
        {/* Timing Bar Chart */}
        <div className="space-y-3">
          {timingBreakdown.map((item, idx) => {
            const percentage = (item.time / totalTime) * 100;
            return (
              <div key={idx}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="font-medium text-gray-700 dark:text-gray-300">{item.name}</span>
                  <span className="text-gray-600 dark:text-gray-400">{item.time.toFixed(3)}s ({percentage.toFixed(1)}%)</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${percentage}%` }}
                    transition={{ duration: 0.8, delay: 0.5 + idx * 0.1 }}
                    className={`h-full ${item.color} rounded-full`}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </motion.div>

      {/* Top 5 Articles Selected */}
      {details.top_5 && details.top_5.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700"
        >
          <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
            <TrendingUp className="text-blue-600 dark:text-blue-400" size={24} />
            Top 5 Articles (by Rank Score)
          </h3>
          <div className="space-y-3">
            {details.top_5.map((article, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.6 + idx * 0.05 }}
                className="flex items-start gap-3 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg"
              >
                <div className="flex-shrink-0 w-8 h-8 flex items-center justify-center bg-blue-600 dark:bg-blue-500 text-white rounded-full font-bold text-sm">
                  {idx + 1}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100 line-clamp-2">
                    {article.headline}
                  </p>
                  <div className="flex items-center gap-3 mt-1 text-xs text-gray-600 dark:text-gray-400">
                    <span>{article.source}</span>
                    <span>•</span>
                    <span>Score: {article.rank_score.toFixed(3)}</span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      {/* AI Generated Summary */}
      {details.groq_summary && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="bg-gradient-to-br from-purple-50 to-indigo-50 dark:from-purple-900/20 dark:to-indigo-900/20 p-6 rounded-lg border-2 border-purple-200 dark:border-purple-700"
        >
          <div className="flex items-center gap-2 mb-4">
            <Sparkles className="text-purple-600 dark:text-purple-400" size={24} />
            <h3 className="text-lg font-bold text-purple-900 dark:text-purple-300">AI-Generated Summary (Groq)</h3>
          </div>
          <p className="text-gray-800 dark:text-gray-200 leading-relaxed">{details.groq_summary}</p>
          <div className="mt-3 text-sm text-purple-700 dark:text-purple-400">
            <Cpu size={16} className="inline mr-1" />
            Generated in {(timings.summary_generation || 0).toFixed(2)}s using Groq API
          </div>
        </motion.div>
      )}

      {/* Similarity Scores */}
      {details.top_10_scores && details.top_10_scores.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="bg-white dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-700"
        >
          <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
            <Sparkles className="text-green-600 dark:text-green-400" size={24} />
            Top 10 Similarity Scores
          </h3>
          <div className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            Neural encoding using <span className="font-mono font-semibold text-gray-900 dark:text-gray-100">all-mpnet-base-v2</span>
            <br />
            Threshold: <span className="font-semibold text-gray-900 dark:text-gray-100">{details.threshold || 0.5}</span> | 
            Top-K: <span className="font-semibold text-gray-900 dark:text-gray-100">{details.top_k || 10}</span>
          </div>
          <div className="space-y-2">
            {details.top_10_scores.map((item, idx) => {
              const percentage = item.score * 100;
              const colorClass = percentage >= 70 ? 'bg-green-500' : percentage >= 60 ? 'bg-yellow-500' : 'bg-blue-500';
              return (
                <div key={idx} className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span className="font-medium text-gray-700 dark:text-gray-300 truncate flex-1 pr-2">
                      {idx + 1}. {item.headline}
                    </span>
                    <span className="text-gray-900 dark:text-gray-100 font-bold whitespace-nowrap">
                      {item.score.toFixed(4)}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${percentage}%` }}
                      transition={{ duration: 0.8, delay: 0.9 + idx * 0.05 }}
                      className={`h-full ${colorClass} rounded-full`}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </motion.div>
      )}

      {/* Selection Summary */}
      {details.selection_count && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1 }}
          className="bg-green-50 dark:bg-green-900/20 p-6 rounded-lg border border-green-200 dark:border-green-700"
        >
          <h3 className="text-lg font-bold text-green-900 dark:text-green-300 mb-4">Final Selection</h3>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-3xl font-bold text-green-700 dark:text-green-400">{details.selection_count.top_k}</div>
              <div className="text-sm text-green-600 dark:text-green-500 mt-1">Top-K Articles</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-green-700 dark:text-green-400">{details.selection_count.above_threshold}</div>
              <div className="text-sm text-green-600 dark:text-green-500 mt-1">Above Threshold</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-green-700 dark:text-green-400">{details.selection_count.total_selected}</div>
              <div className="text-sm text-green-600 dark:text-green-500 mt-1">Total Selected</div>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
};

