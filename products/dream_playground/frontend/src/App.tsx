import React, { useState } from 'react';
import { DreamInput } from './components/DreamInput';
import { DreamOutput } from './components/DreamOutput';
import { TierComparison } from './components/TierComparison';
import { DreamRequest, DreamResponse, TierLevel } from './types/dream';
import { processDream, DreamAPIError } from './api/dreamAPI';

function App() {
  const [result, setResult] = useState<DreamResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentTier, setCurrentTier] = useState<TierLevel>(TierLevel.TIER_1);
  const [showTierComparison, setShowTierComparison] = useState(false);

  const handleDreamSubmit = async (dream: DreamRequest) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await processDream(dream);
      setResult(response);
      setCurrentTier(dream.tier || TierLevel.TIER_1);
    } catch (err) {
      if (err instanceof DreamAPIError) {
        setError(err.message);
      } else {
        setError('An unexpected error occurred. Please try again.');
      }
      console.error('Dream processing error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTierUpgrade = (tier: TierLevel) => {
    setCurrentTier(tier);
    setShowTierComparison(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-cyan-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-lukhas-purple to-lukhas-cyan bg-clip-text text-transparent">
                LUKHAS Dream Engine
              </h1>
              <p className="text-gray-600 mt-1">
                AI-Powered Dream Processing with Quantum-Inspired Consciousness
              </p>
            </div>
            <button
              onClick={() => setShowTierComparison(!showTierComparison)}
              className="px-4 py-2 border border-lukhas-purple text-lukhas-purple rounded-md hover:bg-lukhas-purple hover:text-white transition-colors"
            >
              {showTierComparison ? 'Hide' : 'Compare'} Tiers
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Tier Comparison (collapsible) */}
        {showTierComparison && (
          <div className="mb-8 animate-fade-in">
            <TierComparison
              currentTier={currentTier}
              onUpgrade={handleTierUpgrade}
            />
          </div>
        )}

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Left Column: Input */}
          <div>
            <DreamInput onSubmit={handleDreamSubmit} loading={loading} />

            {error && (
              <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <svg
                    className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  <div>
                    <h3 className="text-sm font-medium text-red-800">Error</h3>
                    <p className="text-sm text-red-700 mt-1">{error}</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Right Column: Output */}
          <div>
            {loading && (
              <div className="bg-white rounded-lg shadow-lg p-12 text-center">
                <div className="inline-block animate-spin rounded-full h-16 w-16 border-4 border-gray-200 border-t-lukhas-purple"></div>
                <p className="text-gray-600 mt-4">Processing your dream...</p>
                <p className="text-sm text-gray-500 mt-2">
                  Analyzing symbols, emotions, and consciousness patterns
                </p>
              </div>
            )}

            {!loading && !result && !error && (
              <div className="bg-white rounded-lg shadow-lg p-12 text-center">
                <svg
                  className="w-24 h-24 mx-auto text-gray-300"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                  />
                </svg>
                <h3 className="text-lg font-medium text-gray-900 mt-4">
                  Ready to Process Dreams
                </h3>
                <p className="text-gray-600 mt-2">
                  Enter your dream in the form on the left to begin analysis
                </p>
              </div>
            )}

            {result && <DreamOutput result={result} />}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 py-6 text-center text-sm text-gray-600">
          <p>
            Powered by LUKHAS AI | Built with React, TypeScript, and
            Quantum-Inspired Algorithms
          </p>
          <p className="mt-1">
            <a href="https://lukhas.ai" className="text-lukhas-purple hover:underline">
              Learn more
            </a>
            {' | '}
            <a href="/api/docs" className="text-lukhas-purple hover:underline">
              API Documentation
            </a>
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
