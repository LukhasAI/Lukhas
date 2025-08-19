'use client'

import { useEffect } from 'react'
import { useTranslation, detectBrowserLanguage, languages } from '@/lib/i18n'

export function TranslationProvider({ children }: { children: React.ReactNode }) {
  const { language, setLanguage, loadTranslations } = useTranslation()

  useEffect(() => {
    // Load all translations on mount
    loadTranslations()

    // Set initial language from storage or browser detection
    const storedLang = localStorage.getItem('lukhas-language')
    if (storedLang) {
      try {
        const parsed = JSON.parse(storedLang)
        const lang = parsed?.state?.language
        if (lang && languages[lang]) {
          setLanguage(lang)
        } else {
          // If stored language is invalid, use browser detection
          const detectedLang = detectBrowserLanguage()
          setLanguage(detectedLang)
        }
      } catch (e) {
        // If parsing fails, use browser detection
        const detectedLang = detectBrowserLanguage()
        setLanguage(detectedLang)
      }
    } else {
      // No stored language, use browser detection
      const detectedLang = detectBrowserLanguage()
      setLanguage(detectedLang)
    }
  }, [setLanguage, loadTranslations])

  // Ensure we always have a valid language
  useEffect(() => {
    if (!language || !languages[language]) {
      console.warn('Invalid or missing language, setting to English')
      setLanguage('en')
    }
  }, [language, setLanguage])

  return <>{children}</>
}