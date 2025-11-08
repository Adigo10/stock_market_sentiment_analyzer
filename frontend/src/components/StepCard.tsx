import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle2, Loader2, Circle, ChevronDown, ChevronUp } from 'lucide-react';
import { Card } from './Card';

interface StepCardProps {
  stepNumber: number;
  title: string;
  status: 'pending' | 'loading' | 'completed' | 'error';
  summary?: React.ReactNode;
  details?: React.ReactNode;
  expandable?: boolean;
}

export const StepCard: React.FC<StepCardProps> = ({ 
  stepNumber, 
  title, 
  status, 
  summary,
  details,
  expandable = false
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const getStatusIcon = () => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="text-green-500" size={24} />;
      case 'loading':
        return (
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          >
            <Loader2 className="text-blue-500" size={24} />
          </motion.div>
        );
      case 'error':
        return <Circle className="text-red-500" size={24} />;
      default:
        return <Circle className="text-gray-400" size={24} />;
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'completed':
        return 'border-green-500';
      case 'loading':
        return 'border-blue-500';
      case 'error':
        return 'border-red-500';
      default:
        return 'border-gray-300 dark:border-gray-600';
    }
  };

  return (
    <Card animate className={`p-6 border-l-4 ${getStatusColor()}`}>
      <div className="flex items-center gap-4 mb-4">
        {getStatusIcon()}
        <div className="flex-1">
          <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100">
            Step {stepNumber}: {title}
          </h3>
        </div>
      </div>
      
      {summary && (
        <div className="mb-4">
          {summary}
        </div>
      )}

      {expandable && details && (
        <div>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex items-center gap-2 text-blue-600 dark:text-blue-400 font-semibold hover:underline"
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
          
          <AnimatePresence>
            {isExpanded && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.3, ease: 'easeInOut' }}
                className="overflow-hidden"
              >
                <div className="mt-4">
                  {details}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      )}

      {!expandable && details && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          transition={{ duration: 0.3 }}
        >
          {details}
        </motion.div>
      )}
    </Card>
  );
};

