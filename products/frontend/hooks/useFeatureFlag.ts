/**
 * React hook for feature flags.
 *
 * Provides a simple interface to check feature flag status in React components.
 * Handles loading states, errors, and caching.
 *
 * @example
 * ```tsx
 * import { useFeatureFlag } from '@/hooks/useFeatureFlag';
 *
 * function MyComponent() {
 *   const { enabled, loading, error } = useFeatureFlag('reasoning_lab_enabled');
 *
 *   if (loading) return <Spinner />;
 *   if (error) return <ErrorState />;
 *   if (!enabled) return null;
 *
 *   return <NewFeature />;
 * }
 * ```
 */

import { useState, useEffect } from 'react';

interface FeatureFlagHookResult {
  enabled: boolean;
  loading: boolean;
  error: Error | null;
  refetch: () => void;
}

interface FlagEvaluationContext {
  user_id?: string;
  email?: string;
  environment?: string;
}

/**
 * Custom hook to check if a feature flag is enabled.
 *
 * @param flagName - Name of the feature flag
 * @param context - Optional evaluation context (user, environment, etc.)
 * @param options - Hook options (cacheTime, refetchInterval, etc.)
 * @returns Object with enabled status, loading state, and error
 */
export function useFeatureFlag(
  flagName: string,
  context?: FlagEvaluationContext,
  options?: {
    cacheTime?: number;  // Cache time in ms (default: 60000)
    refetchInterval?: number;  // Auto-refetch interval in ms
    enabled?: boolean;  // Enable/disable the hook
  }
): FeatureFlagHookResult {
  const [enabled, setEnabled] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);

  const {
    cacheTime = 60000,  // Default: 1 minute cache
    refetchInterval,
    enabled: hookEnabled = true
  } = options || {};

  const fetchFlag = async () => {
    if (!hookEnabled) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // Check sessionStorage cache first
      const cacheKey = `feature_flag_${flagName}`;
      const cached = sessionStorage.getItem(cacheKey);

      if (cached) {
        const { value, timestamp } = JSON.parse(cached);
        const age = Date.now() - timestamp;

        if (age < cacheTime) {
          setEnabled(value);
          setLoading(false);
          return;
        }
      }

      // Fetch from API
      const apiKey = process.env.NEXT_PUBLIC_API_KEY || '';
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

      const response = await fetch(
        `${apiUrl}/api/features/${flagName}/evaluate`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-API-Key': apiKey,
          },
          body: JSON.stringify(context || {}),
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to fetch flag: ${response.statusText}`);
      }

      const data = await response.json();
      const isEnabled = data.enabled || false;

      // Update state
      setEnabled(isEnabled);

      // Cache result
      sessionStorage.setItem(
        cacheKey,
        JSON.stringify({
          value: isEnabled,
          timestamp: Date.now(),
        })
      );

    } catch (err) {
      setError(err instanceof Error ? err : new Error('Unknown error'));
      setEnabled(false);  // Fail safe: disable on error
    } finally {
      setLoading(false);
    }
  };

  // Initial fetch
  useEffect(() => {
    fetchFlag();
  }, [flagName, JSON.stringify(context), hookEnabled]);

  // Auto-refetch interval
  useEffect(() => {
    if (!refetchInterval) return;

    const interval = setInterval(fetchFlag, refetchInterval);
    return () => clearInterval(interval);
  }, [refetchInterval]);

  return {
    enabled,
    loading,
    error,
    refetch: fetchFlag,
  };
}

/**
 * Hook to get all feature flags (admin only).
 *
 * @returns Object with flags array, loading state, and error
 */
export function useAllFeatureFlags() {
  const [flags, setFlags] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchFlags = async () => {
    try {
      setLoading(true);
      setError(null);

      const apiKey = process.env.NEXT_PUBLIC_API_KEY || '';
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

      const response = await fetch(`${apiUrl}/api/features/`, {
        headers: {
          'X-API-Key': apiKey,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch flags: ${response.statusText}`);
      }

      const data = await response.json();
      setFlags(data.flags || []);

    } catch (err) {
      setError(err instanceof Error ? err : new Error('Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFlags();
  }, []);

  return {
    flags,
    loading,
    error,
    refetch: fetchFlags,
  };
}

/**
 * Hook to update a feature flag (admin only).
 *
 * @returns Function to update flag and mutation state
 */
export function useUpdateFeatureFlag() {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  const updateFlag = async (
    flagName: string,
    updates: { enabled?: boolean; percentage?: number }
  ) => {
    try {
      setLoading(true);
      setError(null);

      const apiKey = process.env.NEXT_PUBLIC_API_KEY || '';
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

      const response = await fetch(`${apiUrl}/api/features/${flagName}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': apiKey,
        },
        body: JSON.stringify(updates),
      });

      if (!response.ok) {
        throw new Error(`Failed to update flag: ${response.statusText}`);
      }

      return await response.json();

    } catch (err) {
      setError(err instanceof Error ? err : new Error('Unknown error'));
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    updateFlag,
    loading,
    error,
  };
}
