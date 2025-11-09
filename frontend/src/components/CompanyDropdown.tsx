import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronRight, Building2, Check, Search } from 'lucide-react';

interface CompanyDropdownProps {
  value: string;
  onChange: (value: string) => void;
  options: string[];
  disabled?: boolean;
  className?: string;
}

interface CompanyLogoInfo {
  path: string;
  needsInvert: boolean; // For logos that are black and need to be white in dark mode
}

const companyLogos: Record<string, CompanyLogoInfo> = {
  Apple: { path: '/logos/apple-logo-svgrepo-com.svg', needsInvert: true },
  NVIDIA: { path: '/logos/nvidia-logo-svgrepo-com.svg', needsInvert: true },
  Google: { path: '/logos/google-svgrepo-com.svg', needsInvert: false },
  Microsoft: { path: '/logos/microsoft-svgrepo-com.svg', needsInvert: true },
  Meta: { path: '/logos/meta-svgrepo-com.svg', needsInvert: true },
  Amazon: { path: '/logos/amazon-color-svgrepo-com.svg', needsInvert: false },
  Intel: { path: '/logos/intel-svgrepo-com.svg', needsInvert: true },
  AMD: { path: '/logos/amd-svgrepo-com.svg', needsInvert: true },
  Palantir: { path: '/logos/palantir-svgrepo-com.svg', needsInvert: true },
  'C3.ai': { path: '/logos/C3ai_logo.svg', needsInvert: true },
  Tesla: { path: '/logos/tesla-svgrepo-com.svg', needsInvert: true },
};

const CompanyLogo: React.FC<{ companyName: string; className?: string }> = ({ companyName, className = '' }) => {
  const logoInfo = companyLogos[companyName];
  
  if (!logoInfo) {
    return (
      <div className="w-8 h-8 flex items-center justify-center bg-gray-100 dark:bg-gray-700 rounded-lg">
        <Building2 size={20} className="text-gray-600 dark:text-gray-300" />
      </div>
    );
  }

  return (
    <div className={`w-8 h-8 flex items-center justify-center ${className}`}>
      <img
        src={logoInfo.path}
        alt={`${companyName} logo`}
        className="w-full h-full object-contain"
      />
    </div>
  );
};

const getCompanyIcon = (companyName: string): React.ReactNode => {
  return <CompanyLogo companyName={companyName} />;
};

export const CompanyDropdown: React.FC<CompanyDropdownProps> = ({
  value,
  onChange,
  options,
  disabled = false,
  className = '',
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const dropdownRef = useRef<HTMLDivElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);

  const filteredOptions = options.filter(option =>
    option.toLowerCase().includes(searchTerm.toLowerCase())
  );

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setSearchTerm('');
      }
    };

    const handleEscKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isOpen) {
        setIsOpen(false);
        setSearchTerm('');
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleEscKey);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscKey);
    };
  }, [isOpen]);

  useEffect(() => {
    if (isOpen && searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, [isOpen]);

  const handleSelect = (option: string) => {
    onChange(option);
    setIsOpen(false);
    setSearchTerm('');
  };

  const toggleDropdown = () => {
    if (!disabled) {
      setIsOpen(!isOpen);
      setSearchTerm('');
    }
  };

  return (
    <div ref={dropdownRef} className={`relative ${className}`}>
      {/* Selected Value Display */}
      <motion.button
        type="button"
        onClick={toggleDropdown}
        disabled={disabled}
        whileHover={!disabled ? { scale: 1.01 } : {}}
        whileTap={!disabled ? { scale: 0.99 } : {}}
        className={`
          w-full flex items-center justify-between px-4 py-3 
          bg-white dark:bg-gray-800 
          border-2 border-gray-300 dark:border-gray-600 
          rounded-lg shadow-sm
          text-gray-900 dark:text-gray-100
          transition-all duration-200
          ${!disabled ? 'hover:border-blue-500 dark:hover:border-blue-400 cursor-pointer' : 'opacity-50 cursor-not-allowed'}
          ${isOpen ? 'border-blue-500 dark:border-blue-400 ring-2 ring-blue-500/20' : ''}
        `}
      >
        <div className="flex items-center gap-3">
          {getCompanyIcon(value)}
          <span className="font-medium">{value}</span>
        </div>
        <motion.div
          animate={{ rotate: isOpen ? 180 : 0 }}
          transition={{ duration: 0.2 }}
        >
          {isOpen ? (
            <ChevronRight size={20} className="text-gray-600 dark:text-gray-400" />
          ) : (
            <ChevronDown size={20} className="text-gray-600 dark:text-gray-400" />
          )}
        </motion.div>
      </motion.button>

      {/* Dropdown Panel */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="absolute z-50 w-full mt-2 bg-white dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-600 rounded-lg shadow-xl overflow-hidden"
          >
            {/* Search Input */}
            <div className="p-3 border-b border-gray-200 dark:border-gray-700">
              <div className="relative">
                <Search size={18} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  ref={searchInputRef}
                  type="text"
                  placeholder="Search companies..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-3 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Options List */}
            <div className="max-h-64 overflow-y-auto">
              {filteredOptions.length === 0 ? (
                <div className="px-4 py-8 text-center text-gray-500 dark:text-gray-400">
                  No companies found
                </div>
              ) : (
                filteredOptions.map((option) => (
                  <motion.button
                    key={option}
                    type="button"
                    onClick={() => handleSelect(option)}
                    whileHover={{ backgroundColor: 'rgba(59, 130, 246, 0.1)' }}
                    className={`
                      w-full flex items-center justify-between px-4 py-3 
                      text-left transition-colors duration-150
                      ${value === option ? 'bg-blue-50 dark:bg-blue-900/20' : 'hover:bg-gray-50 dark:hover:bg-gray-700'}
                    `}
                  >
                    <div className="flex items-center gap-3">
                      {getCompanyIcon(option)}
                      <span className="font-medium text-gray-900 dark:text-gray-100">
                        {option}
                      </span>
                    </div>
                    {value === option && (
                      <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                      >
                        <Check size={18} className="text-blue-600 dark:text-blue-400" />
                      </motion.div>
                    )}
                  </motion.button>
                ))
              )}
            </div>

            {/* Panel Footer */}
            <div className="px-4 py-3 bg-gray-50 dark:bg-gray-900/50 border-t border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between text-xs text-gray-600 dark:text-gray-400">
                <span>{filteredOptions.length} companies available</span>
                <span className="text-gray-500 dark:text-gray-500">Press ESC to close</span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

