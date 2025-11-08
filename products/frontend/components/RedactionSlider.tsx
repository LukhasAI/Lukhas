/**
 * Redaction Slider UI Component
 *
 * Interactive slider for controlling redaction level in reasoning traces.
 * Levels: None (0) → Low (25) → Medium (50) → High (75) → Paranoid (100)
 */

import React, { useState, useEffect } from 'react';

interface RedactionLevel {
  value: number;
  label: string;
  description: string;
  mode: 'none' | 'partial' | 'blur' | 'hash' | 'full';
}

const REDACTION_LEVELS: RedactionLevel[] = [
  {
    value: 0,
    label: 'None',
    description: 'No redaction - show all content (use only in secure environments)',
    mode: 'none',
  },
  {
    value: 25,
    label: 'Low',
    description: 'Partial redaction - show first/last chars (e.g., "sk-a...xyz")',
    mode: 'partial',
  },
  {
    value: 50,
    label: 'Medium',
    description: 'Blur redaction - replace with asterisks (e.g., "****-****")',
    mode: 'blur',
  },
  {
    value: 75,
    label: 'High',
    description: 'Hash redaction - show cryptographic hash (e.g., "hash:a1b2...")',
    mode: 'hash',
  },
  {
    value: 100,
    label: 'Paranoid',
    description: 'Full redaction - complete removal (e.g., "[REDACTED-API-KEY]")',
    mode: 'full',
  },
];

interface RedactionSliderProps {
  defaultValue?: number;
  onChange?: (level: RedactionLevel) => void;
  showPreview?: boolean;
  className?: string;
}

export const RedactionSlider: React.FC<RedactionSliderProps> = ({
  defaultValue = 50,
  onChange,
  showPreview = true,
  className = '',
}) => {
  const [value, setValue] = useState<number>(defaultValue);
  const [currentLevel, setCurrentLevel] = useState<RedactionLevel>(
    REDACTION_LEVELS[2]
  );
  const [detectedSensitiveData, setDetectedSensitiveData] = useState<boolean>(false);

  // Load saved preference from localStorage
  useEffect(() => {
    const savedValue = localStorage.getItem('redactionLevel');
    if (savedValue) {
      const parsedValue = parseInt(savedValue, 10);
      setValue(parsedValue);
      updateLevel(parsedValue);
    }
  }, []);

  // Update level when value changes
  useEffect(() => {
    updateLevel(value);
  }, [value]);

  const updateLevel = (newValue: number) => {
    const level = REDACTION_LEVELS.reduce((prev, curr) =>
      Math.abs(curr.value - newValue) < Math.abs(prev.value - newValue)
        ? curr
        : prev
    );

    setCurrentLevel(level);
    localStorage.setItem('redactionLevel', newValue.toString());

    if (onChange) {
      onChange(level);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = parseInt(e.target.value, 10);
    setValue(newValue);
  };

  const getSliderColor = () => {
    if (value === 0) return '#ef4444'; // red - dangerous
    if (value <= 25) return '#f97316'; // orange - caution
    if (value <= 50) return '#eab308'; // yellow - moderate
    if (value <= 75) return '#22c55e'; // green - safe
    return '#10b981'; // emerald - paranoid
  };

  const exampleText = 'My API key is sk-abc123xyz456';
  const getPreviewText = () => {
    switch (currentLevel.mode) {
      case 'none':
        return exampleText;
      case 'partial':
        return 'My API key is sk-a...456';
      case 'blur':
        return 'My API key is **-*********';
      case 'hash':
        return 'My API key is hash:7f8a9b2c...';
      case 'full':
        return 'My API key is [REDACTED-API-KEY]';
      default:
        return exampleText;
    }
  };

  return (
    <div className={`redaction-slider-container ${className}`}>
      {/* Visual feedback for sensitive data detection */}
      {detectedSensitiveData && (
        <div className="sensitive-data-alert">
          <span className="alert-icon">⚠️</span>
          <span className="alert-text">
            Sensitive data detected - redaction level: {currentLevel.label}
          </span>
        </div>
      )}

      {/* Slider control */}
      <div className="slider-wrapper">
        <label htmlFor="redaction-slider" className="slider-label">
          Redaction Level: <strong>{currentLevel.label}</strong>
        </label>

        <input
          id="redaction-slider"
          type="range"
          min="0"
          max="100"
          step="25"
          value={value}
          onChange={handleChange}
          className="slider"
          style={{ accentColor: getSliderColor() }}
        />

        {/* Level markers */}
        <div className="slider-markers">
          {REDACTION_LEVELS.map((level) => (
            <div
              key={level.value}
              className={`marker ${value === level.value ? 'active' : ''}`}
              style={{ left: `${level.value}%` }}
            >
              <div className="marker-label">{level.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Description tooltip */}
      <div className="level-description">
        <p>{currentLevel.description}</p>
      </div>

      {/* Real-time preview */}
      {showPreview && (
        <div className="redaction-preview">
          <h4>Preview:</h4>
          <div className="preview-box">
            <div className="preview-original">
              <span className="preview-label">Original:</span>
              <code>{exampleText}</code>
            </div>
            <div className="preview-redacted">
              <span className="preview-label">Redacted:</span>
              <code>{getPreviewText()}</code>
            </div>
          </div>
        </div>
      )}

      {/* Styling */}
      <style jsx>{`
        .redaction-slider-container {
          padding: 1.5rem;
          border-radius: 0.5rem;
          background: #f9fafb;
          border: 1px solid #e5e7eb;
        }

        .sensitive-data-alert {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.75rem 1rem;
          background: #fef3c7;
          border: 1px solid #f59e0b;
          border-radius: 0.375rem;
          margin-bottom: 1rem;
        }

        .alert-icon {
          font-size: 1.25rem;
        }

        .alert-text {
          font-size: 0.875rem;
          color: #92400e;
        }

        .slider-wrapper {
          margin-bottom: 1.5rem;
        }

        .slider-label {
          display: block;
          margin-bottom: 1rem;
          font-size: 1rem;
          color: #374151;
        }

        .slider {
          width: 100%;
          height: 8px;
          border-radius: 4px;
          background: #e5e7eb;
          outline: none;
          -webkit-appearance: none;
          appearance: none;
        }

        .slider::-webkit-slider-thumb {
          -webkit-appearance: none;
          appearance: none;
          width: 20px;
          height: 20px;
          border-radius: 50%;
          background: currentColor;
          cursor: pointer;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }

        .slider::-moz-range-thumb {
          width: 20px;
          height: 20px;
          border-radius: 50%;
          background: currentColor;
          cursor: pointer;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
          border: none;
        }

        .slider-markers {
          position: relative;
          height: 40px;
          margin-top: 0.5rem;
        }

        .marker {
          position: absolute;
          transform: translateX(-50%);
        }

        .marker-label {
          font-size: 0.75rem;
          color: #6b7280;
          white-space: nowrap;
        }

        .marker.active .marker-label {
          color: #111827;
          font-weight: 600;
        }

        .level-description {
          padding: 0.75rem 1rem;
          background: white;
          border-radius: 0.375rem;
          border: 1px solid #e5e7eb;
          margin-bottom: 1rem;
        }

        .level-description p {
          margin: 0;
          font-size: 0.875rem;
          color: #6b7280;
        }

        .redaction-preview {
          margin-top: 1.5rem;
        }

        .redaction-preview h4 {
          margin-bottom: 0.75rem;
          font-size: 0.875rem;
          font-weight: 600;
          color: #374151;
        }

        .preview-box {
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 0.375rem;
          padding: 1rem;
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }

        .preview-original,
        .preview-redacted {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
        }

        .preview-label {
          font-size: 0.75rem;
          font-weight: 600;
          color: #6b7280;
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }

        .preview-box code {
          font-family: 'Monaco', 'Menlo', monospace;
          font-size: 0.875rem;
          padding: 0.5rem;
          background: #f3f4f6;
          border-radius: 0.25rem;
          color: #111827;
        }
      `}</style>
    </div>
  );
};

export default RedactionSlider;
