import React from 'react';
import type { SentimentType } from '@/types';
import { normalizeSentimentType } from '@/utils/helpers';

interface BadgeProps {
  sentiment: SentimentType;
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
}

export const SentimentBadge: React.FC<BadgeProps> = ({ 
  sentiment, 
  size = 'md',
  showIcon = true 
}) => {
  const normalized = normalizeSentimentType(sentiment);
  
  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-3 py-1 text-sm',
    lg: 'px-4 py-1.5 text-base',
  };

  const colorClasses = {
    positive: 'bg-green-100 text-green-800 border-green-200 dark:bg-green-900/30 dark:text-green-400 dark:border-green-800',
    negative: 'bg-red-100 text-red-800 border-red-200 dark:bg-red-900/30 dark:text-red-400 dark:border-red-800',
    neutral: 'bg-gray-100 text-gray-800 border-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600',
  };

  const icons = {
    positive: '🟢',
    negative: '🔴',
    neutral: '⚪',
  };

  const labels = {
    positive: 'Positive',
    negative: 'Negative',
    neutral: 'Neutral',
  };

  return (
    <span className={`inline-flex items-center gap-1 font-semibold rounded-full border ${sizeClasses[size]} ${colorClasses[normalized]}`}>
      {showIcon && <span>{icons[normalized]}</span>}
      <span>{labels[normalized]}</span>
    </span>
  );
};

interface KeyphraseBadgeProps {
  phrase: string;
  confidence: number;
  type: 'positive' | 'negative' | 'neutral';
}

export const KeyphraseBadge: React.FC<KeyphraseBadgeProps> = ({ phrase, confidence, type }) => {
  const colorClasses = {
    positive: 'bg-green-50 text-green-700 border-green-200 dark:bg-green-900/20 dark:text-green-400 dark:border-green-800',
    negative: 'bg-red-50 text-red-700 border-red-200 dark:bg-red-900/20 dark:text-red-400 dark:border-red-800',
    neutral: 'bg-gray-50 text-gray-700 border-gray-200 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-700',
  };

  return (
    <span 
      className={`inline-block px-2.5 py-1 m-1 text-xs font-medium rounded-md border ${colorClasses[type]}`}
      title={`Confidence: ${confidence.toFixed(2)}`}
    >
      {phrase}
    </span>
  );
};

