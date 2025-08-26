/*
 * ═══════════════════════════════════════════════════════════════════════════
 * FILENAME: OracleChat.tsx
 * MODULE: frontend.src.components
 * DESCRIPTION: Oracle chat component for Oneiric Core dream generation and
 *              analysis. Provides interface for dream prompt input, recursive
 *              analysis options, and real-time dream generation with symbolic
 *              interpretation display.
 * DEPENDENCIES: react, @tanstack/react-query, ../lib/api, ../context/SettingsContext
 * LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
 * ═══════════════════════════════════════════════════════════════════════════
 */

'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { apiFetch } from '../lib/api';
import { useSettings } from '../context/SettingsContext';

interface DreamResponse {
  sceneId: string;
  narrativeText: string;
  renderedImageUrl: string;
  narrativeAudioUrl?: string;
  symbolicStructure: {
    visualAnchor: string;
    directive_used: string;
    driftAnalysis?: {
      driftScore: number;
    };
  };
}

export default function OracleChat() {
  const [prompt, setPrompt] = useState('');
  const { isRecursionEnabled } = useSettings();

  const dreamMutation = useMutation({
    mutationFn: async (data: { prompt: string; recursive: boolean }) => {
      const response = await apiFetch('/api/generate-dream', {
        method: 'POST',
        body: JSON.stringify(data),
      });
      return response as DreamResponse;
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (prompt.trim()) {
      dreamMutation.mutate({
        prompt: prompt.trim(),
        recursive: isRecursionEnabled
      });
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <form onSubmit={handleSubmit} className="mb-8">
        <div className="relative">
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe your dream intention, symbolic query, or emotional state..."
            className="w-full p-4 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows={4}
            disabled={dreamMutation.isPending}
          />
          <div className="absolute bottom-3 right-3 flex items-center space-x-2">
            {isRecursionEnabled && (
              <span className="text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded">
                Recursive Mode
              </span>
            )}
            <button
              type="submit"
              disabled={dreamMutation.isPending || !prompt.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {dreamMutation.isPending ? 'Dreaming...' : 'Generate Dream'}
            </button>
          </div>
        </div>
      </form>

      {dreamMutation.isError && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800 text-sm">
            Error generating dream. Please try again.
          </p>
        </div>
      )}

      {dreamMutation.isPending && (
        <div className="mb-6 p-6 bg-gray-50 rounded-lg">
          <div className="flex items-center space-x-3">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
            <div>
              <p className="text-gray-800 font-medium">Generating dream...</p>
              <p className="text-gray-600 text-sm">
                Synthesizing symbolic content from your subconscious
              </p>
            </div>
          </div>
        </div>
      )}

      {dreamMutation.data && (
        <div className="mb-6 p-6 bg-white rounded-lg border shadow-sm animate-fadeUp">
          <img
            src={dreamMutation.data.renderedImageUrl}
            alt={dreamMutation.data.symbolicStructure.visualAnchor}
            className="w-full h-64 object-cover rounded-md mb-4"
          />

          <h3 className="font-bold mb-2 text-gray-900">
            Dream: {dreamMutation.data.sceneId.slice(0, 8)}
          </h3>

          <p className="text-gray-700 mb-4 leading-relaxed">
            {dreamMutation.data.narrativeText}
          </p>

          {dreamMutation.data.narrativeAudioUrl && (
            <audio controls src={dreamMutation.data.narrativeAudioUrl} className="w-full mb-4">
              Your browser does not support the audio element.
            </audio>
          )}

          <div className="flex flex-wrap gap-2 text-xs mb-4">
            <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
              Directive: {dreamMutation.data.symbolicStructure.directive_used}
            </span>

            {dreamMutation.data.symbolicStructure.driftAnalysis && (
              <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded-full">
                Drift: {dreamMutation.data.symbolicStructure.driftAnalysis.driftScore}
              </span>
            )}

            <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full">
              Anchor: {dreamMutation.data.symbolicStructure.visualAnchor}
            </span>
          </div>

          <div className="pt-4 border-t">
            <p className="text-xs text-gray-600">
              Dream generated • View in journal for rating options
            </p>
          </div>
        </div>
      )}

      <div className="mt-8 p-4 bg-gray-100 rounded-lg text-center text-sm text-gray-600">
        <p>
          ═══════════════════════════════════════════════════════════════════════════
        </p>
        <p>
          FILENAME: OracleChat.tsx
        </p>
        <p>
          VERSION: 1.0.0
        </p>
        <p>
          TIER SYSTEM: Frontend dream interface (Interactive layer for all user tiers)
        </p>
        <p>
          ΛTRACE INTEGRATION: ENABLED
        </p>
        <p>
          CAPABILITIES: Dream generation, prompt processing, recursive analysis, symbolic
          interpretation display, settings integration, error handling
        </p>
        <p>
          FUNCTIONS: OracleChat (default export), handleSubmit, dream generation API calls
        </p>
        <p>
          CLASSES: None directly defined (React functional component)
        </p>
        <p>
          DECORATORS: 'use client' directive for client-side rendering
        </p>
        <p>
          DEPENDENCIES: React hooks, TanStack Query, API layer, settings context
        </p>
        <p>
          INTERFACES: DreamResponse, form event handling, mutation interface
        </p>
        <p>
          ERROR HANDLING: API error display, loading states, validation
        </p>
        <p>
          LOGGING: ΛTRACE_ENABLED for user interactions and dream generation tracking
        </p>
        <p>
          AUTHENTICATION: Uses API layer for authenticated requests
        </p>
        <p>
          HOW TO USE:
        </p>
        <p>
          &nbsp;&nbsp;&nbsp;&nbsp;<OracleChat />
        </p>
        <p>
          &nbsp;&nbsp;&nbsp;&nbsp;Automatically integrates with settings context for recursion options
        </p>
        <p>
          &nbsp;&nbsp;&nbsp;&nbsp;Handles dream prompt submission and displays generated content
        </p>
        <p>
          INTEGRATION NOTES: Core interactive component for Oneiric Core dream analysis.
        </p>
        <p>
          &nbsp;&nbsp;&nbsp;&nbsp;Integrates with backend API for dream generation, provides real-time feedback,
        </p>
        <p>
          &nbsp;&nbsp;&nbsp;&nbsp;and displays symbolic analysis results with visual anchors.
        </p>
        <p>
          MAINTENANCE: Update dream interface as API evolves, maintain responsive design,
        </p>
        <p>
          &nbsp;&nbsp;&nbsp;&nbsp;enhance error messaging, integrate new dream analysis features.
        </p>
        <p>
          CONTACT: LUKHAS DEVELOPMENT TEAM
        </p>
        <p>
          LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
        </p>
        <p>
          ═══════════════════════════════════════════════════════════════════════════
        </p>
      </div>
    </div>
  );
}
