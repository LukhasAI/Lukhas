'use client';

import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/Button';
import { 
  Keyboard,
  Command,
  X,
  Zap,
  Settings,
  Crown,
  Maximize2,
  Search
} from 'lucide-react';

interface KeyboardShortcutsProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function KeyboardShortcuts({ isOpen, onClose }: KeyboardShortcutsProps) {
  const [pressedKeys, setPressedKeys] = useState<Set<string>>(new Set());

  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      setPressedKeys(prev => new Set([...Array.from(prev), e.key.toLowerCase()]));
    };

    const handleKeyUp = (e: KeyboardEvent) => {
      setPressedKeys(prev => {
        const newSet = new Set(prev);
        newSet.delete(e.key.toLowerCase());
        return newSet;
      });
    };

    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('keyup', handleKeyUp);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('keyup', handleKeyUp);
    };
  }, [isOpen]);

  if (!isOpen) return null;

  const shortcuts = [
    {
      category: 'Navigation',
      icon: Command,
      shortcuts: [
        { keys: ['Space'], description: 'Toggle fullscreen mode', icon: Maximize2 },
        { keys: ['⌘', 'K'], description: 'Open command palette', icon: Search },
        { keys: ['⌘', '['], description: 'Toggle left sidebar', icon: null },
        { keys: ['⌘', ']'], description: 'Toggle right sidebar', icon: null },
      ]
    },
    {
      category: 'System',
      icon: Zap,
      shortcuts: [
        { keys: ['⌘', ','], description: 'Open settings', icon: Settings },
        { keys: ['⌘', 'B'], description: 'Open branding', icon: Crown },
        { keys: ['⌘', '?'], description: 'Show shortcuts', icon: Keyboard },
        { keys: ['Esc'], description: 'Close current modal', icon: X },
      ]
    },
    {
      category: 'Chat',
      icon: Keyboard,
      shortcuts: [
        { keys: ['Enter'], description: 'Send message', icon: null },
        { keys: ['Shift', 'Enter'], description: 'New line', icon: null },
        { keys: ['⌘', '1'], description: 'Chat mode', icon: null },
        { keys: ['⌘', '2'], description: 'Code mode', icon: null },
      ]
    }
  ];

  const isKeyPressed = (key: string) => pressedKeys.has(key.toLowerCase());

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center">
      <div className="bg-[var(--surface)] border border-[var(--border)] rounded-2xl p-6 w-[500px] max-h-[80vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <Keyboard size={20} className="text-accent" />
            <h2 className="text-xl font-semibold text-[var(--text-primary)]">Keyboard Shortcuts</h2>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose} className="p-1">
            <X size={18} />
          </Button>
        </div>

        {/* Live key display */}
        {pressedKeys.size > 0 && (
          <div className="mb-6 p-3 bg-accent/10 border border-accent/20 rounded-lg">
            <div className="text-sm text-accent mb-2">Currently pressed:</div>
            <div className="flex gap-2 flex-wrap">
              {Array.from(pressedKeys).map(key => (
                <kbd key={key} className="px-2 py-1 bg-accent/20 text-accent rounded text-sm font-mono">
                  {key === ' ' ? 'Space' : key}
                </kbd>
              ))}
            </div>
          </div>
        )}

        {/* Shortcuts */}
        <div className="space-y-6">
          {shortcuts.map((category) => {
            const CategoryIcon = category.icon;
            return (
              <div key={category.category}>
                <h3 className="text-sm font-medium text-[var(--text-primary)] mb-3 flex items-center gap-2">
                  <CategoryIcon size={16} />
                  {category.category}
                </h3>
                <div className="space-y-2">
                  {category.shortcuts.map((shortcut, index) => {
                    const ShortcutIcon = shortcut.icon;
                    const allPressed = shortcut.keys.every(key => 
                      isKeyPressed(key.replace('⌘', 'meta').replace('Shift', 'shift'))
                    );
                    
                    return (
                      <div 
                        key={index} 
                        className={`flex items-center justify-between p-3 rounded-lg transition-all duration-200 ${
                          allPressed ? 'bg-accent/20 border border-accent/30' : 'bg-[var(--background)] border border-[var(--border)]'
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          {ShortcutIcon && <ShortcutIcon size={16} className="text-[var(--text-secondary)]" />}
                          <span className={`text-sm ${allPressed ? 'text-accent font-medium' : 'text-[var(--text-primary)]'}`}>
                            {shortcut.description}
                          </span>
                        </div>
                        <div className="flex gap-1">
                          {shortcut.keys.map((key, keyIndex) => (
                            <kbd 
                              key={keyIndex}
                              className={`px-2 py-1 rounded text-xs font-mono transition-all duration-200 ${
                                isKeyPressed(key.replace('⌘', 'meta').replace('Shift', 'shift'))
                                  ? 'bg-accent text-white scale-110'
                                  : 'bg-[var(--surface)] text-[var(--text-secondary)] border border-[var(--border)]'
                              }`}
                            >
                              {key}
                            </kbd>
                          ))}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>

        {/* Tips */}
        <div className="mt-6 pt-4 border-t border-[var(--border)]">
          <div className="text-xs text-[var(--text-secondary)] space-y-1">
            <div>💡 <strong>Tip:</strong> Try pressing keys to see them highlight above</div>
            <div>⚡ <strong>Pro:</strong> Hold ⌘ while clicking for quick actions</div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end pt-4 mt-4 border-t border-[var(--border)]">
          <Button size="sm" onClick={onClose}>
            Got it!
          </Button>
        </div>
      </div>
    </div>
  );
}