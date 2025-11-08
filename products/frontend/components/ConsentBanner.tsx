/**
 * GDPR-compliant consent banner component
 *
 * Features:
 * - Accept/Reject/Customize controls
 * - Granular consent management
 * - Privacy policy link
 * - Opt-out at any time
 * - WCAG 2.1 AA compliant
 * - localStorage (no cookies) for preferences
 */

import React, { useState, useEffect } from 'react';

interface ConsentPreferences {
  analytics: boolean;
  marketing: boolean;
  functional: boolean;
  timestamp: string;
}

interface ConsentBannerProps {
  privacyPolicyUrl?: string;
  onConsentChange?: (preferences: ConsentPreferences) => void;
}

const CONSENT_STORAGE_KEY = 'lukhas_analytics_consent';

export const ConsentBanner: React.FC<ConsentBannerProps> = ({
  privacyPolicyUrl = '/privacy',
  onConsentChange,
}) => {
  const [showBanner, setShowBanner] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  const [preferences, setPreferences] = useState<ConsentPreferences>({
    analytics: false,
    marketing: false,
    functional: true, // Essential - always enabled
    timestamp: new Date().toISOString(),
  });

  // Check if consent has been given
  useEffect(() => {
    const stored = localStorage.getItem(CONSENT_STORAGE_KEY);
    if (!stored) {
      setShowBanner(true);
    } else {
      try {
        const parsed = JSON.parse(stored) as ConsentPreferences;
        setPreferences(parsed);
        onConsentChange?.(parsed);
      } catch (e) {
        setShowBanner(true);
      }
    }
  }, [onConsentChange]);

  const saveConsent = (newPreferences: ConsentPreferences) => {
    const withTimestamp = {
      ...newPreferences,
      timestamp: new Date().toISOString(),
    };

    localStorage.setItem(CONSENT_STORAGE_KEY, JSON.stringify(withTimestamp));
    setPreferences(withTimestamp);
    onConsentChange?.(withTimestamp);
    setShowBanner(false);
  };

  const acceptAll = () => {
    saveConsent({
      analytics: true,
      marketing: true,
      functional: true,
      timestamp: new Date().toISOString(),
    });
  };

  const rejectAll = () => {
    saveConsent({
      analytics: false,
      marketing: false,
      functional: true, // Essential cookies cannot be disabled
      timestamp: new Date().toISOString(),
    });
  };

  const saveCustom = () => {
    saveConsent(preferences);
  };

  if (!showBanner) {
    return null;
  }

  return (
    <div
      role="dialog"
      aria-labelledby="consent-banner-title"
      aria-describedby="consent-banner-description"
      className="consent-banner"
      style={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        backgroundColor: '#1a1a2e',
        color: '#ffffff',
        padding: '24px',
        boxShadow: '0 -4px 12px rgba(0, 0, 0, 0.3)',
        zIndex: 9999,
        fontFamily: 'system-ui, -apple-system, sans-serif',
      }}
    >
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <h2
          id="consent-banner-title"
          style={{
            fontSize: '20px',
            fontWeight: 600,
            marginBottom: '12px',
          }}
        >
          Privacy & Analytics Preferences
        </h2>

        <p
          id="consent-banner-description"
          style={{
            fontSize: '14px',
            lineHeight: '1.6',
            marginBottom: '16px',
            opacity: 0.9,
          }}
        >
          We use privacy-first analytics to understand how you interact with our
          platform. <strong>No personal data is collected.</strong> All tracking
          is anonymous and aggregated. You have full control over your
          preferences.
        </p>

        {!showDetails ? (
          <div
            style={{
              display: 'flex',
              gap: '12px',
              flexWrap: 'wrap',
              alignItems: 'center',
            }}
          >
            <button
              onClick={acceptAll}
              style={{
                backgroundColor: '#00ff88',
                color: '#1a1a2e',
                border: 'none',
                padding: '12px 24px',
                fontSize: '14px',
                fontWeight: 600,
                borderRadius: '6px',
                cursor: 'pointer',
                transition: 'background-color 0.2s',
              }}
              onMouseOver={(e) =>
                (e.currentTarget.style.backgroundColor = '#00dd77')
              }
              onMouseOut={(e) =>
                (e.currentTarget.style.backgroundColor = '#00ff88')
              }
            >
              Accept All
            </button>

            <button
              onClick={rejectAll}
              style={{
                backgroundColor: 'transparent',
                color: '#ffffff',
                border: '2px solid #666',
                padding: '10px 24px',
                fontSize: '14px',
                fontWeight: 600,
                borderRadius: '6px',
                cursor: 'pointer',
                transition: 'border-color 0.2s',
              }}
              onMouseOver={(e) => (e.currentTarget.style.borderColor = '#999')}
              onMouseOut={(e) => (e.currentTarget.style.borderColor = '#666')}
            >
              Reject All
            </button>

            <button
              onClick={() => setShowDetails(true)}
              style={{
                backgroundColor: 'transparent',
                color: '#00ff88',
                border: 'none',
                padding: '12px 24px',
                fontSize: '14px',
                fontWeight: 600,
                textDecoration: 'underline',
                cursor: 'pointer',
              }}
            >
              Customize
            </button>

            <a
              href={privacyPolicyUrl}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                color: '#00ff88',
                fontSize: '14px',
                textDecoration: 'underline',
                marginLeft: 'auto',
              }}
            >
              Privacy Policy
            </a>
          </div>
        ) : (
          <div>
            <div style={{ marginBottom: '20px' }}>
              <ConsentToggle
                label="Analytics"
                description="Helps us understand how you use our platform. No personal data collected."
                checked={preferences.analytics}
                onChange={(checked) =>
                  setPreferences({ ...preferences, analytics: checked })
                }
              />

              <ConsentToggle
                label="Marketing"
                description="Allows us to show you relevant content. No third-party tracking."
                checked={preferences.marketing}
                onChange={(checked) =>
                  setPreferences({ ...preferences, marketing: checked })
                }
              />

              <ConsentToggle
                label="Functional (Essential)"
                description="Required for basic website functionality. Cannot be disabled."
                checked={true}
                onChange={() => {}}
                disabled={true}
              />
            </div>

            <div
              style={{
                display: 'flex',
                gap: '12px',
                flexWrap: 'wrap',
              }}
            >
              <button
                onClick={saveCustom}
                style={{
                  backgroundColor: '#00ff88',
                  color: '#1a1a2e',
                  border: 'none',
                  padding: '12px 24px',
                  fontSize: '14px',
                  fontWeight: 600,
                  borderRadius: '6px',
                  cursor: 'pointer',
                }}
              >
                Save Preferences
              </button>

              <button
                onClick={() => setShowDetails(false)}
                style={{
                  backgroundColor: 'transparent',
                  color: '#ffffff',
                  border: '2px solid #666',
                  padding: '10px 24px',
                  fontSize: '14px',
                  fontWeight: 600,
                  borderRadius: '6px',
                  cursor: 'pointer',
                }}
              >
                Back
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

interface ConsentToggleProps {
  label: string;
  description: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  disabled?: boolean;
}

const ConsentToggle: React.FC<ConsentToggleProps> = ({
  label,
  description,
  checked,
  onChange,
  disabled = false,
}) => {
  return (
    <div
      style={{
        marginBottom: '16px',
        padding: '16px',
        backgroundColor: 'rgba(255, 255, 255, 0.05)',
        borderRadius: '8px',
      }}
    >
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '8px',
        }}
      >
        <label
          style={{
            fontSize: '16px',
            fontWeight: 600,
            cursor: disabled ? 'default' : 'pointer',
          }}
        >
          {label}
        </label>

        <div
          onClick={() => !disabled && onChange(!checked)}
          role="switch"
          aria-checked={checked}
          aria-label={label}
          tabIndex={disabled ? -1 : 0}
          onKeyDown={(e) => {
            if (!disabled && (e.key === ' ' || e.key === 'Enter')) {
              e.preventDefault();
              onChange(!checked);
            }
          }}
          style={{
            width: '48px',
            height: '24px',
            backgroundColor: checked ? '#00ff88' : '#666',
            borderRadius: '12px',
            position: 'relative',
            cursor: disabled ? 'not-allowed' : 'pointer',
            transition: 'background-color 0.2s',
            opacity: disabled ? 0.5 : 1,
          }}
        >
          <div
            style={{
              width: '20px',
              height: '20px',
              backgroundColor: '#ffffff',
              borderRadius: '50%',
              position: 'absolute',
              top: '2px',
              left: checked ? '26px' : '2px',
              transition: 'left 0.2s',
            }}
          />
        </div>
      </div>

      <p
        style={{
          fontSize: '13px',
          opacity: 0.8,
          lineHeight: '1.5',
          margin: 0,
        }}
      >
        {description}
      </p>
    </div>
  );
};

/**
 * Hook to access current consent preferences
 */
export const useConsent = (): ConsentPreferences | null => {
  const [preferences, setPreferences] = useState<ConsentPreferences | null>(
    null
  );

  useEffect(() => {
    const stored = localStorage.getItem(CONSENT_STORAGE_KEY);
    if (stored) {
      try {
        setPreferences(JSON.parse(stored));
      } catch (e) {
        setPreferences(null);
      }
    }
  }, []);

  return preferences;
};

/**
 * Hook to manage consent programmatically
 */
export const useConsentManager = () => {
  const [preferences, setPreferences] = useState<ConsentPreferences | null>(
    null
  );

  useEffect(() => {
    const stored = localStorage.getItem(CONSENT_STORAGE_KEY);
    if (stored) {
      try {
        setPreferences(JSON.parse(stored));
      } catch (e) {
        setPreferences(null);
      }
    }
  }, []);

  const updateConsent = (newPreferences: Partial<ConsentPreferences>) => {
    const updated = {
      ...preferences,
      ...newPreferences,
      timestamp: new Date().toISOString(),
    } as ConsentPreferences;

    localStorage.setItem(CONSENT_STORAGE_KEY, JSON.stringify(updated));
    setPreferences(updated);
  };

  const clearConsent = () => {
    localStorage.removeItem(CONSENT_STORAGE_KEY);
    setPreferences(null);
  };

  return {
    preferences,
    updateConsent,
    clearConsent,
    hasAnalyticsConsent: preferences?.analytics ?? false,
    hasMarketingConsent: preferences?.marketing ?? false,
  };
};

export default ConsentBanner;
