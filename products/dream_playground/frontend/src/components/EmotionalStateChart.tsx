import React from 'react';
import { EmotionalState } from '../types/dream';

interface EmotionalStateProps {
  state: EmotionalState;
}

export const EmotionalStateChart: React.FC<EmotionalStateProps> = ({ state }) => {
  const dimensions = [
    { name: 'Valence', value: state.valence, normalized: (state.valence + 1) / 2 },
    { name: 'Arousal', value: state.arousal, normalized: state.arousal },
    { name: 'Dominance', value: state.dominance, normalized: state.dominance },
    { name: 'Intensity', value: state.intensity, normalized: state.intensity },
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <span className="text-2xl">{getEmotionEmoji(state.primary_emotion)}</span>
        <div>
          <div className="font-medium text-gray-900">{state.primary_emotion}</div>
          <div className="text-sm text-gray-500">Primary Emotion</div>
        </div>
      </div>

      <div className="space-y-3">
        {dimensions.map((dim) => (
          <div key={dim.name}>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-700">{dim.name}</span>
              <span className="text-gray-500">
                {dim.value.toFixed(2)}
              </span>
            </div>
            <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-lukhas-blue to-lukhas-cyan transition-all duration-300"
                style={{ width: `${dim.normalized * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

function getEmotionEmoji(emotion: string): string {
  const emojiMap: Record<string, string> = {
    joy: '😊',
    sadness: '😢',
    anger: '😠',
    fear: '😨',
    surprise: '😲',
    neutral: '😐',
    excitement: '🤩',
    peace: '😌',
  };
  return emojiMap[emotion.toLowerCase()] || '🤔';
}
