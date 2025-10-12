'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface SettingsContextType {
  isRecursionEnabled: boolean;
  setRecursionEnabled: (enabled: boolean) => void;
  isDriftLoggingEnabled: boolean;
  setDriftLoggingEnabled: (enabled: boolean) => void;
}

const SettingsContext = createContext<SettingsContextType | undefined>(undefined);

export const SettingsProvider = ({ children }: { children: ReactNode }) => {
  const [isRecursionEnabled, setRecursionEnabled] = useState(true);
  const [isDriftLoggingEnabled, setDriftLoggingEnabled] = useState(true);

  // Load settings from localStorage on mount
  useEffect(() => {
    try {
      const savedRecursion = localStorage.getItem('oneiric_recursion');
      const savedDrift = localStorage.getItem('oneiric_drift');

      if (savedRecursion !== null) {
        setRecursionEnabled(savedRecursion === 'true');
      }

      if (savedDrift !== null) {
        setDriftLoggingEnabled(savedDrift === 'true');
      }
    } catch (error) {
      console.warn('Failed to load settings from localStorage:', error);
    }
  }, []);

  // Save settings to localStorage when they change
  useEffect(() => {
    try {
      localStorage.setItem('oneiric_recursion', String(isRecursionEnabled));
    } catch (error) {
      console.warn('Failed to save recursion setting:', error);
    }
  }, [isRecursionEnabled]);

  useEffect(() => {
    try {
      localStorage.setItem('oneiric_drift', String(isDriftLoggingEnabled));
    } catch (error) {
      console.warn('Failed to save drift setting:', error);
    }
  }, [isDriftLoggingEnabled]);

  const value = {
    isRecursionEnabled,
    setRecursionEnabled,
    isDriftLoggingEnabled,
    setDriftLoggingEnabled,
  };

  return (
    <SettingsContext.Provider value={value}>
      {children}
    </SettingsContext.Provider>
  );
};

export const useSettings = (): SettingsContextType => {
  const context = useContext(SettingsContext);
  if (context === undefined) {
    throw new Error('useSettings must be used within a SettingsProvider');
  }
  return context;
};
