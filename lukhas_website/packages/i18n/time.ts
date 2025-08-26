/**
 * LUKHAS AI - Time Formatting Utilities
 *
 * Utilities for formatting time remaining, parsing Retry-After headers,
 * and handling countdown displays with internationalization support.
 */

interface TimeComponents {
  hours: number;
  minutes: number;
  seconds: number;
}

interface TimeFormatOptions {
  showHours?: boolean;
  showSeconds?: boolean;
  compact?: boolean;
  locale?: 'en' | 'es';
}

/**
 * Parse time in milliseconds to components
 */
export function parseTimeComponents(milliseconds: number): TimeComponents {
  const totalSeconds = Math.max(0, Math.floor(milliseconds / 1000));

  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;

  return { hours, minutes, seconds };
}

/**
 * Format time left for countdown display
 *
 * @param milliseconds - Time remaining in milliseconds
 * @param options - Formatting options
 * @returns Formatted time string
 */
export function formatTimeLeft(
  milliseconds: number,
  options: TimeFormatOptions = {}
): string {
  const {
    showHours = false,
    showSeconds = true,
    compact = true,
    locale = 'en'
  } = options;

  const { hours, minutes, seconds } = parseTimeComponents(milliseconds);

  if (compact) {
    // Compact format: "5m 30s", "90s", "2h 15m"
    const parts: string[] = [];

    if (hours > 0 || showHours) {
      parts.push(`${hours}h`);
    }

    if (minutes > 0 || (hours === 0 && showSeconds === false)) {
      parts.push(`${minutes}m`);
    }

    if (showSeconds && (seconds > 0 || (hours === 0 && minutes === 0))) {
      parts.push(`${seconds}s`);
    }

    return parts.join(' ') || '0s';
  }

  // Full format with locale support
  const formatters = {
    en: {
      hour: (n: number) => n === 1 ? 'hour' : 'hours',
      minute: (n: number) => n === 1 ? 'minute' : 'minutes',
      second: (n: number) => n === 1 ? 'second' : 'seconds'
    },
    es: {
      hour: (n: number) => n === 1 ? 'hora' : 'horas',
      minute: (n: number) => n === 1 ? 'minuto' : 'minutos',
      second: (n: number) => n === 1 ? 'segundo' : 'segundos'
    }
  };

  const formatter = formatters[locale];
  const parts: string[] = [];

  if (hours > 0) {
    parts.push(`${hours} ${formatter.hour(hours)}`);
  }

  if (minutes > 0) {
    parts.push(`${minutes} ${formatter.minute(minutes)}`);
  }

  if (showSeconds && seconds > 0) {
    parts.push(`${seconds} ${formatter.second(seconds)}`);
  }

  if (parts.length === 0) {
    return showSeconds ? `0 ${formatter.second(0)}` : `0 ${formatter.minute(0)}`;
  }

  // Join with commas and "and" for the last item
  if (parts.length === 1) {
    return parts[0];
  }

  const connector = locale === 'es' ? 'y' : 'and';
  const lastPart = parts.pop();
  return `${parts.join(', ')} ${connector} ${lastPart}`;
}

/**
 * Parse Retry-After header value
 *
 * @param retryAfter - Retry-After header value (seconds or HTTP date)
 * @returns Milliseconds until retry is allowed, or null if invalid
 */
export function parseRetryAfter(retryAfter: string | number | null): number | null {
  if (!retryAfter) return null;

  if (typeof retryAfter === 'number') {
    return retryAfter * 1000; // Convert seconds to milliseconds
  }

  const retryAfterStr = retryAfter.toString().trim();

  // Try parsing as seconds (integer)
  const seconds = parseInt(retryAfterStr, 10);
  if (!isNaN(seconds) && seconds >= 0) {
    return seconds * 1000;
  }

  // Try parsing as HTTP date
  try {
    const date = new Date(retryAfterStr);
    if (!isNaN(date.getTime())) {
      const now = Date.now();
      const retryTime = date.getTime();
      return Math.max(0, retryTime - now);
    }
  } catch (error) {
    // Ignore date parsing errors
  }

  return null;
}

/**
 * Calculate time until a future timestamp
 *
 * @param futureTimestamp - Future timestamp in milliseconds
 * @returns Milliseconds until the timestamp, or 0 if in the past
 */
export function timeUntil(futureTimestamp: number): number {
  return Math.max(0, futureTimestamp - Date.now());
}

/**
 * Format seconds to human readable time
 *
 * @param seconds - Seconds to format
 * @param locale - Locale for formatting
 * @returns Formatted string
 */
export function formatSeconds(seconds: number, locale: 'en' | 'es' = 'en'): string {
  return formatTimeLeft(seconds * 1000, { locale, compact: true });
}

/**
 * Get relative time string (e.g., "in 5 minutes", "5 minutes ago")
 *
 * @param timestamp - Timestamp to compare against
 * @param locale - Locale for formatting
 * @returns Relative time string
 */
export function getRelativeTime(timestamp: number, locale: 'en' | 'es' = 'en'): string {
  const now = Date.now();
  const diff = timestamp - now;
  const absDiff = Math.abs(diff);

  const timeStr = formatTimeLeft(absDiff, { locale, compact: false });

  if (diff > 0) {
    return locale === 'es' ? `en ${timeStr}` : `in ${timeStr}`;
  } else if (diff < 0) {
    return locale === 'es' ? `hace ${timeStr}` : `${timeStr} ago`;
  } else {
    return locale === 'es' ? 'ahora' : 'now';
  }
}

/**
 * Create a countdown timer that calls a callback with formatted time
 *
 * @param endTime - End timestamp in milliseconds
 * @param callback - Callback to call with formatted time remaining
 * @param options - Formatting options
 * @returns Function to stop the timer
 */
export function createCountdown(
  endTime: number,
  callback: (timeLeft: string, millisLeft: number) => void,
  options: TimeFormatOptions = {}
): () => void {
  const intervalId = setInterval(() => {
    const remaining = timeUntil(endTime);

    if (remaining <= 0) {
      callback(formatTimeLeft(0, options), 0);
      clearInterval(intervalId);
      return;
    }

    callback(formatTimeLeft(remaining, options), remaining);
  }, 1000);

  // Initial call
  const remaining = timeUntil(endTime);
  callback(formatTimeLeft(remaining, options), remaining);

  return () => clearInterval(intervalId);
}

/**
 * Utility for rate limit display
 *
 * @param resetTime - Reset timestamp in milliseconds
 * @param locale - Locale for formatting
 * @returns Object with formatted time and whether it's expired
 */
export function formatRateLimit(resetTime: number, locale: 'en' | 'es' = 'en') {
  const remaining = timeUntil(resetTime);
  const expired = remaining <= 0;

  return {
    remaining,
    expired,
    formatted: expired
      ? (locale === 'es' ? 'disponible ahora' : 'available now')
      : formatTimeLeft(remaining, { locale, compact: true }),
    relative: expired
      ? (locale === 'es' ? 'expirado' : 'expired')
      : getRelativeTime(resetTime, locale)
  };
}

/**
 * Constants for common time intervals
 */
export const TIME_CONSTANTS = {
  SECOND: 1000,
  MINUTE: 60 * 1000,
  HOUR: 60 * 60 * 1000,
  DAY: 24 * 60 * 60 * 1000,
  WEEK: 7 * 24 * 60 * 60 * 1000
} as const;

/**
 * Default cooldown period for resend operations (30 seconds)
 */
export const DEFAULT_RESEND_COOLDOWN = 30 * TIME_CONSTANTS.SECOND;

export default {
  formatTimeLeft,
  parseRetryAfter,
  timeUntil,
  formatSeconds,
  getRelativeTime,
  createCountdown,
  formatRateLimit,
  parseTimeComponents,
  TIME_CONSTANTS,
  DEFAULT_RESEND_COOLDOWN
};
