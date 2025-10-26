/**
 * LUKHAS AI - Resend Control Component
 * 
 * Real-time countdown, rate limiting, and enumeration-safe responses
 * for verification code resend functionality with full accessibility support.
 */

'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, Mail, AlertTriangle, CheckCircle, Clock } from 'lucide-react';
import { createCountdown, formatTimeLeft, parseRetryAfter, DEFAULT_RESEND_COOLDOWN } from '@/packages/i18n/time';
import { cn } from '@/lib/utils';

// Import rate limiting and email help i18n
import rateI18n from '@/locales/auth.rate.json';
import emailHelpI18n from '@/locales/auth.help.email.json';

interface ResendControlProps {
  /** Email address to send code to */
  email: string;
  /** Purpose of the verification code */
  purpose?: 'login' | 'register' | 'password-reset' | 'email-verification' | 'phone-verification';
  /** Language for i18n */
  locale?: 'en' | 'es';
  /** Channel for code delivery */
  channel?: 'email' | 'sms';
  /** User tier for rate limiting */
  userTier?: 'T1' | 'T2' | 'T3' | 'T4' | 'T5';
  /** Custom cooldown period in milliseconds */
  cooldownMs?: number;
  /** Callback when code is sent successfully */
  onCodeSent?: (result: { requestId: string; success: boolean }) => void;
  /** Callback when rate limit is exceeded */
  onRateLimited?: (resetTime: number) => void;
  /** Custom API endpoint */
  endpoint?: string;
  /** Additional CSS classes */
  className?: string;
  /** Show help text */
  showHelp?: boolean;
  /** Variant for different UI contexts */
  variant?: 'default' | 'compact' | 'minimal';
}

type ResendState = 'idle' | 'sending' | 'cooldown' | 'success' | 'error' | 'rate-limited';

interface ApiResponse {
  ok: boolean;
  message: string;
  requestId: string;
  debug?: {
    codeGenerated: boolean;
    expiresAt: string;
    expiresIn: number;
    channel: string;
    purpose: string;
  };
}

export function ResendControl({
  email,
  purpose = 'login',
  locale = 'en',
  channel = 'email',
  userTier,
  cooldownMs = DEFAULT_RESEND_COOLDOWN,
  onCodeSent,
  onRateLimited,
  endpoint = '/api/auth/code/send',
  className,
  showHelp = true,
  variant = 'default'
}: ResendControlProps) {
  const [state, setState] = useState<ResendState>('idle');
  const [timeLeft, setTimeLeft] = useState<string>('');
  const [millisecondsLeft, setMillisecondsLeft] = useState<number>(0);
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [requestId, setRequestId] = useState<string>('');
  const [rateLimitResetTime, setRateLimitResetTime] = useState<number>(0);
  const [remainingAttempts, setRemainingAttempts] = useState<number | null>(null);
  
  const countdownRef = useRef<(() => void) | null>(null);
  const statusRef = useRef<HTMLDivElement>(null);
  
  // Get localized strings
  const t = rateI18n[locale];
  const helpT = emailHelpI18n[locale];

  // Cleanup countdown on unmount
  useEffect(() => {
    return () => {
      if (countdownRef.current) {
        countdownRef.current();
      }
    };
  }, []);

  // Start countdown timer
  const startCountdown = useCallback((endTime: number) => {
    if (countdownRef.current) {
      countdownRef.current();
    }

    countdownRef.current = createCountdown(
      endTime,
      (formatted, remaining) => {
        setTimeLeft(formatted);
        setMillisecondsLeft(remaining);
        
        if (remaining <= 0) {
          setState('idle');
          setTimeLeft('');
          countdownRef.current = null;
        }
      },
      { locale, compact: true }
    );
  }, [locale]);

  // Handle API response
  const handleResponse = useCallback(async (response: Response) => {
    // Check for rate limiting headers
    const retryAfter = response.headers.get('Retry-After');
    const rateLimitRemaining = response.headers.get('X-RateLimit-Remaining');
    const rateLimitReset = response.headers.get('X-RateLimit-Reset');
    
    if (retryAfter) {
      const retryMs = parseRetryAfter(retryAfter);
      if (retryMs && retryMs > 0) {
        const resetTime = Date.now() + retryMs;
        setRateLimitResetTime(resetTime);
        setState('rate-limited');
        startCountdown(resetTime);
        onRateLimited?.(resetTime);
        return;
      }
    }
    
    if (rateLimitRemaining) {
      setRemainingAttempts(parseInt(rateLimitRemaining, 10));
    }

    const data: ApiResponse = await response.json();
    
    if (response.ok && data.ok) {
      setState('success');
      setRequestId(data.requestId);
      onCodeSent?.({ requestId: data.requestId, success: true });
      
      // Start client-side cooldown
      const cooldownEndTime = Date.now() + cooldownMs;
      setState('cooldown');
      startCountdown(cooldownEndTime);
    } else {
      setState('error');
      setErrorMessage(data.message || t.errors.generic.message);
    }
  }, [startCountdown, cooldownMs, onCodeSent, onRateLimited, t.errors.generic.message]);

  // Send verification code
  const sendCode = useCallback(async () => {
    if (state === 'sending' || state === 'cooldown') return;

    setState('sending');
    setErrorMessage('');
    setRequestId('');

    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          purpose,
          language: locale,
          channel,
          userTier,
        }),
      });

      await handleResponse(response);
    } catch (error) {
      console.error('[ResendControl] Network error:', error);
      setState('error');
      setErrorMessage(t.errors.network.message);
    }
  }, [state, endpoint, email, purpose, locale, channel, userTier, handleResponse, t.errors.network.message]);

  // Get button text based on state
  const getButtonText = (): string => {
    switch (state) {
      case 'sending':
        return t.resend.sending.button;
      case 'cooldown':
        return t.resend.cooldown.button.replace('{time}', timeLeft);
      case 'success':
        return t.resend.success.button;
      case 'error':
        return t.resend.error.button;
      case 'rate-limited':
        return t.resend.cooldown.button.replace('{time}', timeLeft);
      default:
        return t.resend.idle.button;
    }
  };

  // Get status message
  const getStatusMessage = (): string => {
    switch (state) {
      case 'sending':
        return t.resend.sending.message;
      case 'cooldown':
        return t.resend.cooldown.message.replace('{time}', timeLeft);
      case 'success':
        return t.resend.success.message;
      case 'error':
        return errorMessage || t.resend.error.message;
      case 'rate-limited':
        return t.rateLimit.exceeded.message.replace('{time}', timeLeft);
      default:
        return t.resend.idle.message;
    }
  };

  // Get button variant and disabled state
  const isDisabled = state === 'sending' || state === 'cooldown' || state === 'rate-limited';
  const buttonVariant = state === 'error' ? 'destructive' : state === 'success' ? 'default' : 'outline';

  // Get appropriate icon
  const getIcon = () => {
    switch (state) {
      case 'sending':
        return <Loader2 className="w-4 h-4 animate-spin" />;
      case 'success':
        return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'error':
        return <AlertTriangle className="w-4 h-4 text-red-600" />;
      case 'rate-limited':
        return <Clock className="w-4 h-4 text-orange-600" />;
      case 'cooldown':
        return <Clock className="w-4 h-4 text-blue-600" />;
      default:
        return channel === 'email' ? <Mail className="w-4 h-4" /> : null;
    }
  };

  if (variant === 'minimal') {
    return (
      <Button
        onClick={sendCode}
        disabled={isDisabled}
        variant={buttonVariant}
        size="sm"
        className={cn('gap-2', className)}
        data-tone="plain"
      >
        {getIcon()}
        {getButtonText()}
      </Button>
    );
  }

  return (
    <div className={cn('space-y-4', className)} data-tone="plain">
      {/* Resend Button */}
      <div className="flex flex-col sm:flex-row gap-2 items-start sm:items-center">
        <Button
          onClick={sendCode}
          disabled={isDisabled}
          variant={buttonVariant}
          className="gap-2 min-w-[120px]"
          data-tone="plain"
        >
          {getIcon()}
          {getButtonText()}
        </Button>
        
        {variant !== 'compact' && (
          <span className="text-sm text-muted-foreground" data-tone="plain">
            {getStatusMessage()}
          </span>
        )}
      </div>

      {/* Status Messages */}
      <div
        ref={statusRef}
        className="space-y-2"
        role="status"
        aria-live="polite"
        aria-label={t.accessibility.statusRegion}
        data-tone="plain"
      >
        {/* Success Message */}
        {state === 'success' && (
          <Alert className="border-green-200 bg-green-50" data-tone="plain">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-800" data-tone="plain">
              {t.resend.success.detail}
              {requestId && (
                <div className="text-xs mt-1 font-mono opacity-75" data-tone="technical">
                  Request ID: {requestId}
                </div>
              )}
            </AlertDescription>
          </Alert>
        )}

        {/* Error Message */}
        {state === 'error' && (
          <Alert variant="destructive" data-tone="plain">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription data-tone="plain">
              {errorMessage}
            </AlertDescription>
          </Alert>
        )}

        {/* Rate Limit Warning */}
        {state === 'rate-limited' && (
          <Alert className="border-orange-200 bg-orange-50" data-tone="plain">
            <Clock className="h-4 w-4 text-orange-600" />
            <AlertDescription className="text-orange-800" data-tone="plain">
              <div className="font-medium">{t.rateLimit.exceeded.title}</div>
              <div className="text-sm mt-1">
                {t.rateLimit.exceeded.message.replace('{time}', timeLeft)}
              </div>
              <div className="text-xs mt-2 opacity-75" data-tone="technical">
                {t.rateLimit.exceeded.help}
              </div>
            </AlertDescription>
          </Alert>
        )}

        {/* Rate Limit Approaching Warning */}
        {remainingAttempts !== null && remainingAttempts <= 2 && remainingAttempts > 0 && state !== 'rate-limited' && (
          <Alert className="border-yellow-200 bg-yellow-50" data-tone="plain">
            <AlertTriangle className="h-4 w-4 text-yellow-600" />
            <AlertDescription className="text-yellow-800" data-tone="plain">
              <div className="font-medium">{t.rateLimit.approaching.title}</div>
              <div className="text-sm mt-1">
                {t.rateLimit.approaching.message
                  .replace('{remaining}', remainingAttempts.toString())
                  .replace('{limit}', '5')}
              </div>
            </AlertDescription>
          </Alert>
        )}
      </div>

      {/* Countdown Display for Screen Readers */}
      {millisecondsLeft > 0 && (
        <div 
          className="sr-only" 
          aria-live="polite"
          aria-label={t.accessibility.countdown.replace('{time}', timeLeft)}
          data-tone="technical"
        >
          {t.accessibility.countdown.replace('{time}', timeLeft)}
        </div>
      )}
    </div>
  );
}

export default ResendControl;