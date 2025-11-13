import React, { useState } from 'react';
import { DreamRequest, TierLevel } from '../types/dream';
import { getExampleDreams } from '../api/dreamAPI';

interface DreamInputProps {
  onSubmit: (dream: DreamRequest) => void;
  loading: boolean;
}

export const DreamInput: React.FC<DreamInputProps> = ({ onSubmit, loading }) => {
  const [content, setContent] = useState('');
  const [qiEnhanced, setQiEnhanced] = useState(true);
  const [tier, setTier] = useState<TierLevel>(TierLevel.TIER_1);
  const [examples] = useState<string[]>([
    "I was flying over a vast ocean...",
    "In a dark forest, I found a glowing door...",
    "I was solving an impossible puzzle made of stars...",
  ]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (content.trim()) {
      onSubmit({
        content: content.trim(),
        qi_enhanced: qiEnhanced,
        tier,
      });
    }
  };

  const loadExample = (example: string) => {
    setContent(example);
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">
        Process Your Dream
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="dream-content" className="block text-sm font-medium text-gray-700 mb-2">
            Dream Content
          </label>
          <textarea
            id="dream-content"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Describe your dream here..."
            rows={6}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-lukhas-purple focus:border-transparent"
            disabled={loading}
          />
          <p className="mt-1 text-sm text-gray-500">
            {content.length} / 5000 characters
          </p>
        </div>

        <div className="flex gap-2">
          <span className="text-sm text-gray-600">Examples:</span>
          {examples.map((example, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => loadExample(example)}
              className="text-sm text-lukhas-purple hover:underline"
              disabled={loading}
            >
              {idx + 1}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-4">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={qiEnhanced}
              onChange={(e) => setQiEnhanced(e.target.checked)}
              className="rounded border-gray-300 text-lukhas-purple focus:ring-lukhas-purple"
              disabled={loading}
            />
            <span className="ml-2 text-sm text-gray-700">
              Quantum-Inspired Enhancement
            </span>
          </label>

          <select
            value={tier}
            onChange={(e) => setTier(e.target.value as TierLevel)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-lukhas-purple"
            disabled={loading}
          >
            <option value={TierLevel.TIER_1}>Tier 1 (Basic)</option>
            <option value={TierLevel.TIER_2}>Tier 2 (Advanced)</option>
            <option value={TierLevel.TIER_3}>Tier 3 (Pro)</option>
          </select>
        </div>

        <button
          type="submit"
          disabled={loading || !content.trim()}
          className="w-full bg-lukhas-purple text-white py-3 px-6 rounded-md hover:bg-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Processing...
            </span>
          ) : (
            'Process Dream'
          )}
        </button>
      </form>
    </div>
  );
};
