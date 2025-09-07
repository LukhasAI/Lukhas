'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { Theme, GlassOverlay, ThemeContextType } from '@/types';
import { applyTheme, getStoredTheme, getSystemTheme } from '@/lib/themes';

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>('dark');
  const [glassOverlay, setGlassOverlay] = useState<GlassOverlay>(false);

  useEffect(() => {
    const { theme: storedTheme, glassOverlay: storedGlassOverlay } = getStoredTheme();
    const initialTheme = storedTheme || getSystemTheme();
    
    setTheme(initialTheme);
    setGlassOverlay(storedGlassOverlay);
    applyTheme(initialTheme, storedGlassOverlay);
  }, []);

  const handleSetTheme = (newTheme: Theme) => {
    setTheme(newTheme);
    applyTheme(newTheme, glassOverlay);
  };

  const toggleGlassOverlay = () => {
    const newGlassOverlay = !glassOverlay;
    setGlassOverlay(newGlassOverlay);
    applyTheme(theme, newGlassOverlay);
  };

  const value: ThemeContextType = {
    theme,
    glassOverlay,
    setTheme: handleSetTheme,
    toggleGlassOverlay,
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};