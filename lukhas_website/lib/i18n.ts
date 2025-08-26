'use client'

import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export type Language = 'en' | 'es' | 'fr' | 'it' | 'de' | 'pt' | 'zh' | 'ja'

export interface LanguageConfig {
  code: Language
  name: string
  nativeName: string
  flag: string
  direction: 'ltr' | 'rtl'
}

export const languages: Record<Language, LanguageConfig> = {
  en: { code: 'en', name: 'English', nativeName: 'English', flag: '🇬🇧', direction: 'ltr' },
  es: { code: 'es', name: 'Spanish', nativeName: 'Español', flag: '🇪🇸', direction: 'ltr' },
  fr: { code: 'fr', name: 'French', nativeName: 'Français', flag: '🇫🇷', direction: 'ltr' },
  it: { code: 'it', name: 'Italian', nativeName: 'Italiano', flag: '🇮🇹', direction: 'ltr' },
  de: { code: 'de', name: 'German', nativeName: 'Deutsch', flag: '🇩🇪', direction: 'ltr' },
  pt: { code: 'pt', name: 'Portuguese', nativeName: 'Português', flag: '🇵🇹', direction: 'ltr' },
  zh: { code: 'zh', name: 'Chinese', nativeName: '中文', flag: '🇨🇳', direction: 'ltr' },
  ja: { code: 'ja', name: 'Japanese', nativeName: '日本語', flag: '🇯🇵', direction: 'ltr' },
}

interface TranslationStore {
  language: Language
  setLanguage: (lang: Language) => void
  translations: Record<Language, any>
  t: (key: string, vars?: Record<string, string>) => string
  loadTranslations: () => Promise<void>
}

// Create the translation store
export const useTranslation = create<TranslationStore>()(
  persist(
    (set, get) => ({
      language: 'en' as Language,
      translations: {} as Record<Language, any>,

      setLanguage: (lang: Language) => {
        // Validate that the language exists
        if (!languages[lang]) {
          console.warn(`Invalid language: ${lang}, falling back to 'en'`)
          lang = 'en'
        }
        set({ language: lang })
        document.documentElement.lang = lang
        document.documentElement.dir = languages[lang]?.direction || 'ltr'
      },

      t: (key: string, vars?: Record<string, string>) => {
        const state = get()
        const currentLang = state.language || 'en'

        // Return key if translations not loaded yet
        if (!state.translations || Object.keys(state.translations).length === 0) {
          return key
        }

        const keys = key.split('.')
        let value = state.translations[currentLang]

        for (const k of keys) {
          value = value?.[k]
        }

        if (typeof value !== 'string') {
          // Fallback to English if translation not found
          value = state.translations.en
          for (const k of keys) {
            value = value?.[k]
          }
        }

        if (typeof value !== 'string') {
          console.warn(`Translation key not found: ${key}`)
          return key
        }

        // Replace variables
        if (vars) {
          Object.entries(vars).forEach(([varKey, varValue]) => {
            value = value.replace(`{{${varKey}}}`, varValue)
          })
        }

        return value
      },

      loadTranslations: async () => {
        const loadedTranslations: Record<Language, any> = {} as any

        // Load all translation files
        for (const lang of Object.keys(languages) as Language[]) {
          try {
            const module = await import(`../locales/${lang}.json`)
            loadedTranslations[lang] = module.default
          } catch (error) {
            console.warn(`Failed to load translations for ${lang}`)
            // Use English as fallback
            if (lang !== 'en') {
              try {
                const enModule = await import(`../locales/en.json`)
                loadedTranslations[lang] = enModule.default
              } catch (e) {
                console.error('Failed to load English translations')
              }
            }
          }
        }

        set({ translations: loadedTranslations })
      }
    }),
    {
      name: 'lukhas-language',
      partialize: (state) => ({ language: state.language })
    }
  )
)

// Helper hook for using translations
export function useT() {
  const { t, language } = useTranslation()
  return { t, language }
}

// Helper function to detect browser language
export function detectBrowserLanguage(): Language {
  if (typeof window === 'undefined') return 'en'

  const browserLang = navigator.language.toLowerCase()

  // Map browser language codes to our supported languages
  const langMap: Record<string, Language> = {
    'en': 'en',
    'es': 'es',
    'fr': 'fr',
    'it': 'it',
    'de': 'de',
    'pt': 'pt',
    'zh': 'zh',
    'ja': 'ja',
    'en-us': 'en',
    'en-gb': 'en',
    'es-es': 'es',
    'es-mx': 'es',
    'fr-fr': 'fr',
    'it-it': 'it',
    'de-de': 'de',
    'pt-pt': 'pt',
    'pt-br': 'pt',
    'zh-cn': 'zh',
    'zh-tw': 'zh',
    'ja-jp': 'ja',
  }

  // Check full code first, then just the language part
  return langMap[browserLang] || langMap[browserLang.split('-')[0]] || 'en'
}
