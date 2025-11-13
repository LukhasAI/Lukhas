import React from 'react';
import { DreamResponse } from '../types/dream';
import { EmotionalStateChart } from './EmotionalStateChart';

interface DreamOutputProps {
  result: DreamResponse;
}

export const DreamOutput: React.FC<DreamOutputProps> = ({ result }) => {
  const coherencePercent = Math.round(result.quantum_coherence * 100);

  return (
    <div className="space-y-6">
      {/* Processing Stats */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-3xl font-bold text-lukhas-purple">
              {coherencePercent}%
            </div>
            <div className="text-sm text-gray-600">Quantum Coherence</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-lukhas-blue">
              {result.processing_time_ms}ms
            </div>
            <div className="text-sm text-gray-600">Processing Time</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-lukhas-cyan">
              {result.symbolic_annotations.length}
            </div>
            <div className="text-sm text-gray-600">Symbols Detected</div>
          </div>
        </div>

        {/* Coherence Bar */}
        <div className="mt-4">
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-lukhas-purple to-lukhas-cyan transition-all duration-500"
              style={{ width: `${coherencePercent}%` }}
            />
          </div>
        </div>
      </div>

      {/* Processed Content */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-semibold mb-3">Processed Dream</h3>
        <p className="text-gray-700 leading-relaxed">
          {result.processed_content}
        </p>
      </div>

      {/* Emotional State */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-semibold mb-3">Emotional Analysis</h3>
        <EmotionalStateChart state={result.emotional_state} />
      </div>

      {/* Symbolic Annotations */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-semibold mb-3">Symbolic Patterns</h3>
        <div className="space-y-3">
          {result.symbolic_annotations.map((annotation, idx) => (
            <div
              key={idx}
              className="border-l-4 border-lukhas-purple pl-4 py-2"
            >
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="font-medium text-gray-900">{annotation.symbol}</h4>
                  <p className="text-sm text-gray-600 mt-1">{annotation.meaning}</p>
                  <p className="text-xs text-gray-500 mt-1 italic">{annotation.context}</p>
                </div>
                <span className="text-xs bg-lukhas-purple/10 text-lukhas-purple px-2 py-1 rounded">
                  {Math.round(annotation.confidence * 100)}%
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Metadata */}
      <div className="bg-gray-50 rounded-lg p-4 text-sm text-gray-600">
        <div className="flex justify-between">
          <span>Dream ID: {result.dream_id}</span>
          <span>Tier: {result.tier.toUpperCase().replace('_', ' ')}</span>
          <span>{new Date(result.timestamp).toLocaleString()}</span>
        </div>
      </div>
    </div>
  );
};
