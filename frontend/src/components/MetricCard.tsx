import React from 'react';
import { motion } from 'framer-motion';
import { Card } from './Card';

interface MetricCardProps {
  label: string;
  value: string | number;
  icon?: React.ReactNode;
  delay?: number;
}

export const MetricCard: React.FC<MetricCardProps> = ({ label, value, icon, delay = 0 }) => {
  return (
    <Card animate delay={delay} className="p-4">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
            {label}
          </p>
          <motion.p
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: delay + 0.2 }}
            className="text-2xl font-bold text-gray-900 dark:text-gray-100"
          >
            {value}
          </motion.p>
        </div>
        {icon && (
          <div className="text-3xl ml-4">
            {icon}
          </div>
        )}
      </div>
    </Card>
  );
};

