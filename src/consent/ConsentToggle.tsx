/**
 * ConsentToggle - Embeddable React Component for Consent Management
 * Provides GDPR-compliant consent collection with receipt previews
 */

import React, { useState, useCallback, useEffect } from 'react';
import { generateHMAC } from '../utils/hmac';

export interface ConsentScope {
  id: string;
  name: string;
  description: string;
  purpose: string;
  required: boolean;
  category: 'essential' | 'functional' | 'analytics' | 'marketing';
  recipients?: string[];
  retention_period?: string;
}

export interface ConsentReceiptPreview {
  consent_id: string;
  user_id: string;
  scopes: string[];
  granted_at: string;
  expires_at: string;
  policy_version: string;
  signature: string;
  withdrawal_method: string;
  explanations: Record<string, string>;
}

export interface ConsentToggleProps {
  scope: string;
  user_id?: string;
  api_base?: string;
  api_key?: string;
  initial_state?: boolean;
  onConsentChange?: (granted: boolean, receipt?: ConsentReceiptPreview) => void;
  onError?: (error: string) => void;
  theme?: 'light' | 'dark' | 'auto';
  size?: 'small' | 'medium' | 'large';
  show_receipt_preview?: boolean;
  className?: string;
  disabled?: boolean;
}

const defaultScopes: Record<string, ConsentScope> = {
  'opportunity.matching': {
    id: 'opportunity.matching',
    name: 'Opportunity Matching',
    description: 'Match relevant commercial opportunities to your interests',
    purpose: 'Personalized commerce recommendations',
    required: false,
    category: 'functional',
    recipients: ['LUKHAS AI', 'Partner merchants'],
    retention_period: '2 years or until withdrawn'
  },
  'ads.personalized': {
    id: 'ads.personalized',
    name: 'Personalized Advertising',
    description: 'Show personalized advertisements based on your preferences',
    purpose: 'Targeted advertising delivery',
    required: false,
    category: 'marketing',
    recipients: ['LUKHAS AI', 'Advertising partners'],
    retention_period: '1 year or until withdrawn'
  },
  'analytics.usage': {
    id: 'analytics.usage',
    name: 'Usage Analytics',
    description: 'Analyze how you use our platform to improve services',
    purpose: 'Service improvement and optimization',
    required: false,
    category: 'analytics',
    recipients: ['LUKHAS AI'],
    retention_period: '2 years (anonymized after 6 months)'
  },
  'amazon.orders.read': {
    id: 'amazon.orders.read',
    name: 'Amazon Order History',
    description: 'Access your Amazon order history for restock recommendations',
    purpose: 'Intelligent restock suggestions',
    required: false,
    category: 'functional',
    recipients: ['LUKHAS AI'],
    retention_period: '90 days or until withdrawn'
  }
};

export const ConsentToggle: React.FC<ConsentToggleProps> = ({
  scope,
  user_id,
  api_base = 'https://api.lukhas.ai',
  api_key,
  initial_state = false,
  onConsentChange,
  onError,
  theme = 'auto',
  size = 'medium',
  show_receipt_preview = true,
  className = '',
  disabled = false
}) => {
  const [granted, setGranted] = useState(initial_state);
  const [loading, setLoading] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [receiptPreview, setReceiptPreview] = useState<ConsentReceiptPreview | null>(null);
  const [error, setError] = useState<string | null>(null);

  const scopeConfig = defaultScopes[scope];
  
  useEffect(() => {
    if (user_id && api_key) {
      fetchCurrentConsent();
    }
  }, [user_id, api_key, scope]);

  const fetchCurrentConsent = async () => {
    try {
      const response = await fetch(`${api_base}/consent/${scope}`, {
        headers: {
          'Authorization': `Bearer ${api_key}`,
          'X-User-ID': user_id || ''
        }
      });

      if (response.ok) {
        const consent = await response.json();
        setGranted(consent.granted);
      }
    } catch (err) {
      console.error('Failed to fetch consent status:', err);
    }
  };

  const generateReceiptPreview = useCallback((): ConsentReceiptPreview => {
    const now = new Date();
    const expires = new Date(now.getTime() + (365 * 24 * 60 * 60 * 1000)); // 1 year
    
    const receipt: ConsentReceiptPreview = {
      consent_id: `consent_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      user_id: user_id || 'preview_user',
      scopes: [scope],
      granted_at: now.toISOString(),
      expires_at: expires.toISOString(),
      policy_version: '1.2.0',
      signature: 'preview_signature',
      withdrawal_method: 'Visit Settings > Privacy > Consent or email privacy@lukhas.ai',
      explanations: {
        [scope]: scopeConfig?.description || 'Consent for data processing'
      }
    };

    // Generate preview signature (in production, this would be server-side)
    const payload = JSON.stringify({
      user_id: receipt.user_id,
      scopes: receipt.scopes,
      granted_at: receipt.granted_at,
      policy_version: receipt.policy_version
    });
    
    receipt.signature = generateHMAC(payload, 'preview_key').slice(0, 16) + '...';
    
    return receipt;
  }, [scope, user_id, scopeConfig]);

  const handleToggle = async () => {
    if (disabled || loading) return;

    setLoading(true);
    setError(null);

    try {
      if (!granted) {
        // Granting consent - show preview first
        const preview = generateReceiptPreview();
        setReceiptPreview(preview);
        setShowPreview(true);
      } else {
        // Revoking consent
        await revokeConsent();
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to update consent';
      setError(errorMsg);
      onError?.(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const confirmGrant = async () => {
    if (!receiptPreview) return;

    setLoading(true);
    try {
      const response = await fetch(`${api_base}/consent`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${api_key}`,
          'Idempotency-Key': crypto.randomUUID()
        },
        body: JSON.stringify({
          user_id: user_id,
          scopes: [scope],
          policy_version: '1.2.0',
          context: {
            timestamp: new Date().toISOString(),
            user_agent: navigator.userAgent,
            page_url: window.location.href
          }
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      setGranted(true);
      setShowPreview(false);
      onConsentChange?.(true, result.receipt);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to grant consent';
      setError(errorMsg);
      onError?.(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const revokeConsent = async () => {
    try {
      const response = await fetch(`${api_base}/consent/${scope}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${api_key}`,
          'Idempotency-Key': crypto.randomUUID()
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      setGranted(false);
      onConsentChange?.(false);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to revoke consent';
      setError(errorMsg);
      onError?.(errorMsg);
    }
  };

  if (!scopeConfig) {
    return (
      <div className={`consent-toggle-error ${className}`}>
        <span>⚠️ Unknown consent scope: {scope}</span>
      </div>
    );
  }

  const sizeClasses = {
    small: 'text-sm p-2',
    medium: 'text-base p-3', 
    large: 'text-lg p-4'
  };

  const themeClasses = {
    light: 'bg-white text-gray-900 border-gray-300',
    dark: 'bg-gray-800 text-white border-gray-600',
    auto: 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white border-gray-300 dark:border-gray-600'
  };

  return (
    <div className={`consent-toggle-container ${sizeClasses[size]} ${themeClasses[theme]} ${className} border rounded-lg`}>
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 mt-1">
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={granted}
              onChange={handleToggle}
              disabled={disabled || loading}
              className="sr-only"
            />
            <div className={`w-11 h-6 rounded-full transition-colors ${
              granted 
                ? 'bg-blue-600' 
                : 'bg-gray-200 dark:bg-gray-700'
            } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}>
              <div className={`absolute top-0.5 left-0.5 bg-white w-5 h-5 rounded-full transition-transform ${
                granted ? 'transform translate-x-5' : ''
              }`} />
            </div>
          </label>
        </div>

        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <h4 className="font-medium">{scopeConfig.name}</h4>
            {scopeConfig.required && (
              <span className="text-xs px-2 py-1 bg-orange-100 text-orange-800 rounded">
                Required
              </span>
            )}
          </div>
          
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
            {scopeConfig.description}
          </p>

          <div className="text-xs text-gray-500 dark:text-gray-500">
            <span>Recipients: {scopeConfig.recipients?.join(', ')}</span>
            {scopeConfig.retention_period && (
              <span className="ml-3">Retention: {scopeConfig.retention_period}</span>
            )}
          </div>

          {error && (
            <div className="mt-2 text-sm text-red-600 dark:text-red-400">
              {error}
            </div>
          )}
        </div>

        {loading && (
          <div className="flex-shrink-0">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600" />
          </div>
        )}
      </div>

      {/* Receipt Preview Modal */}
      {showPreview && receiptPreview && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-lg w-full mx-4 max-h-[80vh] overflow-y-auto">
            <h3 className="text-lg font-semibold mb-4">Consent Receipt Preview</h3>
            
            <div className="space-y-3 text-sm">
              <div>
                <span className="font-medium">Consent ID:</span>
                <span className="ml-2 font-mono text-xs">{receiptPreview.consent_id}</span>
              </div>
              
              <div>
                <span className="font-medium">Granted for:</span>
                <span className="ml-2">{scopeConfig.name}</span>
              </div>
              
              <div>
                <span className="font-medium">Purpose:</span>
                <span className="ml-2">{scopeConfig.purpose}</span>
              </div>
              
              <div>
                <span className="font-medium">Valid until:</span>
                <span className="ml-2">{new Date(receiptPreview.expires_at).toLocaleDateString()}</span>
              </div>
              
              <div>
                <span className="font-medium">Withdrawal:</span>
                <span className="ml-2">{receiptPreview.withdrawal_method}</span>
              </div>
              
              <div className="pt-2 border-t">
                <span className="font-medium">Digital signature:</span>
                <div className="font-mono text-xs text-gray-600 dark:text-gray-400 break-all">
                  {receiptPreview.signature}
                </div>
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={confirmGrant}
                disabled={loading}
                className="flex-1 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? 'Granting...' : 'Grant Consent'}
              </button>
              <button
                onClick={() => {setShowPreview(false); setLoading(false);}}
                className="flex-1 border border-gray-300 dark:border-gray-600 px-4 py-2 rounded hover:bg-gray-50 dark:hover:bg-gray-700"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

/**
 * Usage Examples:
 * 
 * // Basic usage
 * <ConsentToggle scope="opportunity.matching" />
 * 
 * // With user context and callbacks
 * <ConsentToggle 
 *   scope="amazon.orders.read"
 *   user_id="user_123"
 *   api_key={apiKey}
 *   onConsentChange={(granted, receipt) => {
 *     console.log('Consent changed:', granted, receipt);
 *   }}
 *   onError={(error) => {
 *     console.error('Consent error:', error);
 *   }}
 * />
 * 
 * // Themed and sized
 * <ConsentToggle 
 *   scope="ads.personalized"
 *   theme="dark"
 *   size="large"
 *   show_receipt_preview={true}
 * />
 */

export default ConsentToggle;