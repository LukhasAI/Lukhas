// lib/state/appStateMachine.ts
import { setup } from 'xstate';

// Guards for the state machine
const guards = {
  isEURegion: () => {
    if (typeof window === 'undefined') return false;

    // Try to detect EU region from language, timezone, or other indicators
    const language = navigator.language;
    const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

    const euLanguages = ['de', 'fr', 'it', 'es', 'nl', 'pl', 'pt', 'sv', 'da', 'fi', 'hu', 'cs', 'sk', 'sl', 'hr', 'bg', 'ro', 'et', 'lv', 'lt', 'mt', 'el'];
    const euTimezones = ['Europe/', 'Atlantic/Canary', 'Atlantic/Madeira'];

    const isEULanguage = euLanguages.some(lang => language.toLowerCase().startsWith(lang));
    const isEUTimezone = euTimezones.some(tz => timezone.startsWith(tz));

    return isEULanguage || isEUTimezone;
  },

  isAuthenticated: () => {
    if (typeof window === 'undefined') return false;
    // Check for auth token or session
    return localStorage.getItem('lukhas_auth_token') !== null;
  },

  reducedMotion: () => {
    if (typeof window === 'undefined') return true;
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }
};

// App state machine based on visual_studio.json
export const appStateMachine = setup({
  guards,
}).createMachine({
  id: 'lukhasApp',
  initial: 'BOOT',
  states: {
    BOOT: {
      on: {
        BG_READY: 'QUOTE_IN'
      },
      entry: () => {
        console.log('🚀 LUKHΛS booting...');
      }
    },

    QUOTE_IN: {
      on: {
        CONSENT_NEEDED: {
          target: 'CONSENT_PENDING',
          guard: 'isEURegion'
        },
        SKIP_CONSENT: 'MARKETING_MODE'
      },
      entry: () => {
        console.log('💭 Quote animation starting...');
      }
    },

    CONSENT_PENDING: {
      on: {
        CONSENT_ACCEPTED: 'MARKETING_MODE',
        CONSENT_REJECTED: 'MARKETING_MODE',
        CONSENT_PARTIAL: 'MARKETING_MODE'
      },
      entry: () => {
        console.log('🍪 Consent required - showing cookie preferences');
      }
    },

    MARKETING_MODE: {
      on: {
        CLICK_LOGIN: 'LOGIN_FLOW',
        ENTER_STUDIO_IF_AUTH: {
          target: 'ROUTE_DECISION',
          guard: 'isAuthenticated'
        }
      },
      entry: () => {
        console.log('🎯 Marketing mode - ready for user interaction');
      }
    },

    LOGIN_FLOW: {
      on: {
        TOS_ACCEPTED: 'ROUTE_DECISION',
        TOS_DECLINED: 'MARKETING_MODE'
      },
      entry: () => {
        console.log('🔐 Login flow initiated');
      }
    },

    ROUTE_DECISION: {
      on: {
        FIRST_TIME: 'STUDIO_DEFAULT_PRESET',
        RETURNING: 'STUDIO_USER_PRESET'
      },
      entry: () => {
        console.log('🧭 Determining user route...');
      }
    },

    STUDIO_DEFAULT_PRESET: {
      entry: () => {
        console.log('🎨 Loading default studio preset');
      }
    },

    STUDIO_USER_PRESET: {
      entry: () => {
        console.log('👤 Loading user studio preset');
      }
    }
  }
});

export type AppState = typeof appStateMachine.states;
export type AppEvent =
  | { type: 'BG_READY' }
  | { type: 'CONSENT_NEEDED' }
  | { type: 'SKIP_CONSENT' }
  | { type: 'CONSENT_ACCEPTED' }
  | { type: 'CONSENT_REJECTED' }
  | { type: 'CONSENT_PARTIAL' }
  | { type: 'CLICK_LOGIN' }
  | { type: 'ENTER_STUDIO_IF_AUTH' }
  | { type: 'TOS_ACCEPTED' }
  | { type: 'TOS_DECLINED' }
  | { type: 'FIRST_TIME' }
  | { type: 'RETURNING' };
