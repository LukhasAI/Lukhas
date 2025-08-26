'use client';

import { useSettings } from '../context/SettingsContext';

interface SettingsOverlayProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function SettingsOverlay({ isOpen, onClose }: SettingsOverlayProps) {
  const {
    isRecursionEnabled,
    setRecursionEnabled,
    isDriftLoggingEnabled,
    setDriftLoggingEnabled
  } = useSettings();

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
      <div className="bg-white rounded-lg max-w-md w-full mx-4 p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-gray-900">Settings</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>

        <div className="space-y-6">
          <div>
            <h3 className="text-sm font-medium text-gray-900 mb-3">
              Dream Generation
            </h3>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <label className="text-sm text-gray-700">
                  Recursive Dreaming
                </label>
                <input
                  type="checkbox"
                  checked={isRecursionEnabled}
                  onChange={(e) => setRecursionEnabled(e.target.checked)}
                  className="toggle-switch"
                />
              </div>

              <div className="flex items-center justify-between">
                <label className="text-sm text-gray-700">
                  Drift Logging
                </label>
                <input
                  type="checkbox"
                  checked={isDriftLoggingEnabled}
                  onChange={(e) => setDriftLoggingEnabled(e.target.checked)}
                  className="toggle-switch"
                />
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-sm font-medium text-gray-900 mb-3">
              Experience
            </h3>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <label className="text-sm text-gray-700">
                  Audio Narration
                </label>
                <input
                  type="checkbox"
                  defaultChecked={true}
                  className="toggle-switch"
                />
              </div>

              <div className="flex items-center justify-between">
                <label className="text-sm text-gray-700">
                  Symbolic Overlays
                </label>
                <input
                  type="checkbox"
                  defaultChecked={true}
                  className="toggle-switch"
                />
              </div>
            </div>
          </div>
        </div>

        <div className="mt-8 flex justify-end space-x-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm text-gray-700 bg-gray-100 rounded hover:bg-gray-200"
          >
            Cancel
          </button>
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm text-white bg-blue-600 rounded hover:bg-blue-700"
          >
            Save Changes
          </button>
        </div>
      </div>
    </div>
  );
}
