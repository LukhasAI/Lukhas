/**
 * Feature Flags Admin UI
 *
 * Provides a dashboard for managing feature flags:
 * - View all flags
 * - Toggle boolean flags on/off
 * - Adjust percentage rollouts (slider 0-100%)
 * - View flag evaluation history
 * - Export flag configuration
 *
 * Requires admin role.
 */

import React, { useState } from 'react';
import { useAllFeatureFlags, useUpdateFeatureFlag } from '@/hooks/useFeatureFlag';

interface FlagInfo {
  name: string;
  enabled: boolean;
  flag_type: string;
  description: string;
  owner: string;
  created_at: string;
  jira_ticket: string;
  percentage?: number;
}

export default function FeatureFlagsAdminPage() {
  const { flags, loading, error, refetch } = useAllFeatureFlags();
  const { updateFlag, loading: updating } = useUpdateFeatureFlag();
  const [filter, setFilter] = useState<string>('all');  // all, enabled, disabled

  const handleToggle = async (flagName: string, currentValue: boolean) => {
    try {
      await updateFlag(flagName, { enabled: !currentValue });
      refetch();  // Refresh list
    } catch (err) {
      console.error('Failed to toggle flag:', err);
    }
  };

  const handlePercentageChange = async (flagName: string, percentage: number) => {
    try {
      await updateFlag(flagName, { percentage });
      refetch();
    } catch (err) {
      console.error('Failed to update percentage:', err);
    }
  };

  const exportConfig = () => {
    const config = {
      version: '1.0',
      flags: flags.reduce((acc, flag) => ({
        ...acc,
        [flag.name]: {
          type: flag.flag_type,
          enabled: flag.enabled,
          description: flag.description,
          owner: flag.owner,
          created_at: flag.created_at,
          jira_ticket: flag.jira_ticket,
          ...(flag.percentage !== undefined && { percentage: flag.percentage }),
        },
      }), {}),
      metadata: {
        exported_at: new Date().toISOString(),
        total_flags: flags.length,
      },
    };

    const blob = new Blob([JSON.stringify(config, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `feature-flags-${Date.now()}.json`;
    a.click();
  };

  const filteredFlags = flags.filter(flag => {
    if (filter === 'enabled') return flag.enabled;
    if (filter === 'disabled') return !flag.enabled;
    return true;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="spinner mb-4"></div>
          <p>Loading feature flags...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center text-red-600">
          <h2 className="text-2xl font-bold mb-2">Error Loading Flags</h2>
          <p>{error.message}</p>
          <button
            onClick={() => refetch()}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Feature Flags Admin</h1>
        <div className="flex gap-4">
          <button
            onClick={exportConfig}
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
          >
            Export Config
          </button>
          <button
            onClick={() => refetch()}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            disabled={loading}
          >
            Refresh
          </button>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-4 mb-6 border-b">
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 ${filter === 'all' ? 'border-b-2 border-blue-600 font-bold' : ''}`}
        >
          All ({flags.length})
        </button>
        <button
          onClick={() => setFilter('enabled')}
          className={`px-4 py-2 ${filter === 'enabled' ? 'border-b-2 border-blue-600 font-bold' : ''}`}
        >
          Enabled ({flags.filter(f => f.enabled).length})
        </button>
        <button
          onClick={() => setFilter('disabled')}
          className={`px-4 py-2 ${filter === 'disabled' ? 'border-b-2 border-blue-600 font-bold' : ''}`}
        >
          Disabled ({flags.filter(f => !f.enabled).length})
        </button>
      </div>

      {/* Flags List */}
      <div className="space-y-4">
        {filteredFlags.map((flag: FlagInfo) => (
          <div
            key={flag.name}
            className="border rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow"
          >
            <div className="flex justify-between items-start mb-4">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="text-xl font-semibold">{flag.name}</h3>
                  <span className={`px-2 py-1 text-xs rounded ${
                    flag.enabled ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {flag.enabled ? 'Enabled' : 'Disabled'}
                  </span>
                  <span className="px-2 py-1 text-xs rounded bg-blue-100 text-blue-800">
                    {flag.flag_type}
                  </span>
                </div>
                <p className="text-gray-600 mb-2">{flag.description}</p>
                <div className="text-sm text-gray-500">
                  <p>Owner: {flag.owner}</p>
                  <p>Created: {flag.created_at}</p>
                  <p>Ticket: {flag.jira_ticket}</p>
                </div>
              </div>

              {/* Toggle Switch */}
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={flag.enabled}
                  onChange={() => handleToggle(flag.name, flag.enabled)}
                  disabled={updating}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>

            {/* Percentage Slider for percentage flags */}
            {flag.flag_type === 'percentage' && flag.percentage !== undefined && (
              <div className="mt-4 pt-4 border-t">
                <label className="block text-sm font-medium mb-2">
                  Rollout Percentage: {flag.percentage}%
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={flag.percentage}
                  onChange={(e) => handlePercentageChange(flag.name, parseInt(e.target.value))}
                  disabled={updating || !flag.enabled}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>0%</span>
                  <span>50%</span>
                  <span>100%</span>
                </div>
              </div>
            )}
          </div>
        ))}

        {filteredFlags.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            No {filter !== 'all' && filter} flags found
          </div>
        )}
      </div>
    </div>
  );
}
