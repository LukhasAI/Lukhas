import React from 'react';
import { TierLevel, TIER_COMPARISON } from '../types/dream';

interface TierComparisonProps {
  currentTier: TierLevel;
  onUpgrade?: (tier: TierLevel) => void;
}

export const TierComparison: React.FC<TierComparisonProps> = ({ currentTier, onUpgrade }) => {
  const tiers = [TierLevel.TIER_1, TierLevel.TIER_2, TierLevel.TIER_3];

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
        Choose Your Tier
      </h2>

      <div className="grid md:grid-cols-3 gap-6">
        {tiers.map((tier) => {
          const features = TIER_COMPARISON[tier];
          const isCurrent = tier === currentTier;

          return (
            <div
              key={tier}
              className={`
                relative border-2 rounded-lg p-6 transition-all
                ${isCurrent
                  ? 'border-lukhas-purple bg-lukhas-purple/5 scale-105'
                  : 'border-gray-200 hover:border-lukhas-purple/50'
                }
              `}
            >
              {isCurrent && (
                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-lukhas-purple text-white px-3 py-1 rounded-full text-xs font-medium">
                  Current
                </div>
              )}

              <div className="text-center mb-4">
                <h3 className="text-xl font-bold text-gray-900">{features.name}</h3>
                <div className="text-3xl font-bold text-lukhas-purple mt-2">
                  {features.price}
                </div>
                <div className="text-sm text-gray-500 mt-1">
                  {features.processingSpeed}
                </div>
              </div>

              <ul className="space-y-2 mb-6">
                {features.features.map((feature, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <svg
                      className="w-5 h-5 text-lukhas-purple flex-shrink-0 mt-0.5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                    <span className="text-sm text-gray-700">{feature}</span>
                  </li>
                ))}
              </ul>

              {!isCurrent && onUpgrade && (
                <button
                  onClick={() => onUpgrade(tier)}
                  className="w-full bg-lukhas-purple text-white py-2 px-4 rounded-md hover:bg-purple-700 transition-colors"
                >
                  Select {features.name}
                </button>
              )}

              {isCurrent && (
                <div className="w-full bg-gray-100 text-gray-600 py-2 px-4 rounded-md text-center text-sm font-medium">
                  Active Plan
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="mt-8 text-center text-sm text-gray-500">
        <p>All tiers include secure processing and privacy protection</p>
      </div>
    </div>
  );
};
