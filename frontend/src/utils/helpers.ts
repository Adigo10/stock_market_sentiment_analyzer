import type { Article, ParsedSentiment, SentimentType } from '@/types';

export function parseSentiment(sentimentText: string): ParsedSentiment {
  if (!sentimentText) {
    return { type: 'neutral', reason: '' };
  }

  // Try to extract sentiment using the "Sentiment: " pattern (matching Python logic)
  const sentimentMatch = sentimentText.match(/Sentiment:\s*(\w+)/i);
  const reasonMatch = sentimentText.match(/Reason:\s*(.*)/is);

  let type: SentimentType = 'neutral';
  let reason = '';

  if (sentimentMatch) {
    const extractedType = sentimentMatch[1].toLowerCase();
    // Map "good" to "positive" and "bad" to "negative"
    if (extractedType === 'good' || extractedType === 'positive' || extractedType === 'bullish') {
      type = 'positive';
    } else if (extractedType === 'bad' || extractedType === 'negative' || extractedType === 'bearish') {
      type = 'negative';
    } else if (extractedType === 'neutral' || extractedType === 'okay' || extractedType === 'mixed' || extractedType === 'uncertain') {
      type = 'neutral';
    }
  }

  // Extract reason properly - if found, use it; otherwise return empty string
  if (reasonMatch) {
    reason = reasonMatch[1].trim();
  } else {
    // If no "Reason:" found, check if there's text after sentiment
    if (sentimentMatch) {
      // Get everything after the sentiment declaration
      const remainingText = sentimentText.substring(sentimentMatch.index! + sentimentMatch[0].length).trim();
      // Remove common separators at the start
      reason = remainingText.replace(/^[:\-.,\s]+/, '').trim();
    } else {
      // Fallback: use the entire text if no structure found
      reason = sentimentText.trim();
    }
  }

  return { type, reason };
}

export function normalizeSentimentType(type: SentimentType): 'positive' | 'negative' | 'neutral' {
  const normalized = type.toLowerCase();
  if (normalized === 'good' || normalized === 'positive' || normalized === 'bullish') return 'positive';
  if (normalized === 'bad' || normalized === 'negative' || normalized === 'bearish') return 'negative';
  if (normalized === 'neutral' || normalized === 'okay' || normalized === 'mixed' || normalized === 'uncertain') return 'neutral';
  return 'neutral';
}

export function formatArticleDate(article: Article): string {
  const dateValue = article.datetime || article.publish_date || article.published_date || article.date;
  
  if (!dateValue) return 'Date unknown';

  try {
    const date = new Date(dateValue);
    if (isNaN(date.getTime())) return 'Date unknown';
    
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  } catch {
    return String(dateValue);
  }
}

export function formatTableDate(article: Article): string {
  const dateValue = article.datetime || article.publish_date || article.published_date || article.date;
  
  if (!dateValue) return '-';

  try {
    const date = new Date(dateValue);
    if (isNaN(date.getTime())) return '-';
    
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    });
  } catch {
    return '-';
  }
}

export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
}

export function downloadJSON(data: any, filename: string): void {
  const json = JSON.stringify(data, null, 2);
  const blob = new Blob([json], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

export function getSafeCompanyName(companyName: string): string {
  return companyName.toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '');
}

export function cleanText(text: string): string {
  if (!text) return '';
  
  // Remove special characters and clean up text
  let cleaned = text
    .replace(/[^\w\s.,!?;:()\-'"]/g, '') // Remove special chars except common punctuation
    .replace(/\s+/g, ' ') // Normalize whitespace
    .trim();
  
  // Capitalize first letter if not already
  if (cleaned.length > 0) {
    cleaned = cleaned.charAt(0).toUpperCase() + cleaned.slice(1);
  }
  
  return cleaned;
}

export function formatHeadline(headline: string): string {
  if (!headline) return '';
  
  // Clean the text
  let formatted = cleanText(headline);
  
  // Ensure it ends with proper punctuation if it doesn't
  if (formatted && !/[.!?]$/.test(formatted)) {
    // Don't add period if it looks like a title (all caps or title case)
    const isTitle = formatted === formatted.toUpperCase() || 
                    formatted.split(' ').every(word => word.length === 0 || word[0] === word[0].toUpperCase());
    if (!isTitle) {
      formatted += '.';
    }
  }
  
  return formatted;
}

