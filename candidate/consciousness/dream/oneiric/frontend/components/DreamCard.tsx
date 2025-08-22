'use client';

import { useState } from 'react';
import { Dream } from '../types/dream';
import { useRateDream } from '../lib/hooks';

interface DreamCardProps {
  dream: Dream;
}

export default function DreamCard({ dream }: DreamCardProps) {
  const [feedbackSent, setFeedbackSent] = useState(false);
  const rateMutation = useRateDream();

  const handleRating = (rating: -1 | 0 | 1) => {
    setFeedbackSent(true);
    rateMutation.mutate({ dreamId: dream.sceneId, rating });
  };

  return (
    <div className="border rounded-lg p-4 mb-4 bg-white shadow-sm animate-fadeUp">
      <img
        src={dream.renderedImageUrl}
        alt={dream.symbolicStructure.visualAnchor}
        className="w-full h-64 object-cover rounded-md mb-4"
      />
      
      <h3 className="font-bold mb-2 text-gray-900">
        Dream: {dream.sceneId.slice(0, 8)}
      </h3>
      
      <p className="text-gray-700 mb-4 leading-relaxed">
        {dream.narrativeText}
      </p>
      
      {dream.narrativeAudioUrl && (
        <audio controls src={dream.narrativeAudioUrl} className="w-full mb-4">
          Your browser does not support the audio element.
        </audio>
      )}

      <div className="flex flex-wrap gap-2 text-xs mb-4">
        <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
          Directive: {dream.symbolicStructure.directive_used}
        </span>
        
        {dream.symbolicStructure.driftAnalysis && (
          <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded-full">
            Drift: {dream.symbolicStructure.driftAnalysis.driftScore}
          </span>
        )}
        
        <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full">
          Anchor: {dream.symbolicStructure.visualAnchor}
        </span>
      </div>

      <div className="flex gap-2 pt-4 border-t">
        <button
          onClick={() => handleRating(1)}
          disabled={feedbackSent}
          className="flex-1 p-2 text-xs bg-green-100 text-green-800 rounded hover:bg-green-200 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          👍 Helpful
        </button>
        
        <button
          onClick={() => handleRating(0)}
          disabled={feedbackSent}
          className="flex-1 p-2 text-xs bg-gray-100 text-gray-800 rounded hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          😐 Neutral
        </button>
        
        <button
          onClick={() => handleRating(-1)}
          disabled={feedbackSent}
          className="flex-1 p-2 text-xs bg-red-100 text-red-800 rounded hover:bg-red-200 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          👎 Unhelpful
        </button>
      </div>
      
      {feedbackSent && (
        <p className="text-xs text-gray-600 mt-2 text-center">
          Thank you for your feedback!
        </p>
      )}
    </div>
  );
}
