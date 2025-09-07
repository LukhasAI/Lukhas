'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { 
  Settings as SettingsIcon,
  Monitor,
  Moon,
  Sun,
  Palette,
  Volume2,
  VolumeX,
  Eye,
  EyeOff,
  Keyboard,
  Mouse,
  Wifi,
  Bell,
  BellOff,
  Zap,
  Shield,
  Database,
  Globe,
  X
} from 'lucide-react';

interface SettingsProps {
  isOpen: boolean;
  onClose: () => void;
}

type Theme = 'light' | 'dark' | 'auto';
type GlassOverlay = 'off' | 'subtle' | 'medium' | 'strong';

export default function Settings({ isOpen, onClose }: SettingsProps) {
  const [theme, setTheme] = useState<Theme>('dark');
  const [glassOverlay, setGlassOverlay] = useState<GlassOverlay>('medium');
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [animationsEnabled, setAnimationsEnabled] = useState(true);
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [autoSave, setAutoSave] = useState(true);

  if (!isOpen) return null;

  const handleThemeChange = (newTheme: Theme) => {
    setTheme(newTheme);
    // Apply theme immediately
    if (typeof window !== 'undefined') {
      const root = document.documentElement;
      if (newTheme === 'light') {
        root.style.setProperty('--background', '#FFFFFF');
        root.style.setProperty('--surface', '#F8F9FA');
        root.style.setProperty('--text-primary', '#1A1A1A');
        root.style.setProperty('--text-secondary', '#6B7280');
        root.style.setProperty('--border', 'rgba(0,0,0,0.08)');
      } else if (newTheme === 'dark') {
        root.style.setProperty('--background', '#0B0B0F');
        root.style.setProperty('--surface', '#111216');
        root.style.setProperty('--text-primary', '#FFFFFF');
        root.style.setProperty('--text-secondary', '#C9CDD6');
        root.style.setProperty('--border', 'rgba(255,255,255,0.08)');
      }
    }
  };

  const handleGlassChange = (newGlass: GlassOverlay) => {
    setGlassOverlay(newGlass);
    if (typeof window !== 'undefined') {
      const root = document.documentElement;
      root.classList.toggle('glass-on', newGlass !== 'off');
      root.style.setProperty('--surface-alt', 
        newGlass === 'subtle' ? 'rgba(18,18,24,0.3)' :
        newGlass === 'medium' ? 'rgba(18,18,24,0.6)' :
        newGlass === 'strong' ? 'rgba(18,18,24,0.8)' :
        'rgba(18,18,24,0.6)'
      );
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center">
      <div className="bg-[var(--surface)] border border-[var(--border)] rounded-2xl p-6 w-[500px] max-h-[80vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <SettingsIcon size={20} className="text-accent" />
            <h2 className="text-xl font-semibold text-[var(--text-primary)]">Settings</h2>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose} className="p-1">
            <X size={18} />
          </Button>
        </div>

        {/* Theme Settings */}
        <div className="mb-6">
          <h3 className="text-sm font-medium text-[var(--text-primary)] mb-3 flex items-center gap-2">
            <Palette size={16} />
            Appearance
          </h3>
          <div className="space-y-3">
            <div className="flex gap-2">
              {[
                { id: 'light' as const, label: 'Light', icon: Sun },
                { id: 'dark' as const, label: 'Dark', icon: Moon },
                { id: 'auto' as const, label: 'Auto', icon: Monitor }
              ].map(({ id, label, icon: Icon }) => (
                <Button
                  key={id}
                  variant={theme === id ? "primary" : "ghost"}
                  size="sm"
                  onClick={() => handleThemeChange(id)}
                  className="flex items-center gap-2"
                >
                  <Icon size={14} />
                  {label}
                </Button>
              ))}
            </div>

            <div className="space-y-2">
              <label className="text-xs text-[var(--text-secondary)]">Glass Effect</label>
              <div className="flex gap-2">
                {[
                  { id: 'off' as const, label: 'Off' },
                  { id: 'subtle' as const, label: 'Subtle' },
                  { id: 'medium' as const, label: 'Medium' },
                  { id: 'strong' as const, label: 'Strong' }
                ].map(({ id, label }) => (
                  <Button
                    key={id}
                    variant={glassOverlay === id ? "primary" : "ghost"}
                    size="sm"
                    onClick={() => handleGlassChange(id)}
                    className="text-xs"
                  >
                    {label}
                  </Button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Interface Settings */}
        <div className="mb-6">
          <h3 className="text-sm font-medium text-[var(--text-primary)] mb-3 flex items-center gap-2">
            <Monitor size={16} />
            Interface
          </h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                {soundEnabled ? <Volume2 size={16} /> : <VolumeX size={16} />}
                <span className="text-sm">Sound Effects</span>
              </div>
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => setSoundEnabled(!soundEnabled)}
                className={`p-2 ${soundEnabled ? 'text-accent' : 'text-[var(--text-secondary)]'}`}
              >
                {soundEnabled ? 'On' : 'Off'}
              </Button>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                {animationsEnabled ? <Eye size={16} /> : <EyeOff size={16} />}
                <span className="text-sm">Animations</span>
              </div>
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => setAnimationsEnabled(!animationsEnabled)}
                className={`p-2 ${animationsEnabled ? 'text-accent' : 'text-[var(--text-secondary)]'}`}
              >
                {animationsEnabled ? 'On' : 'Off'}
              </Button>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                {notificationsEnabled ? <Bell size={16} /> : <BellOff size={16} />}
                <span className="text-sm">Notifications</span>
              </div>
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => setNotificationsEnabled(!notificationsEnabled)}
                className={`p-2 ${notificationsEnabled ? 'text-accent' : 'text-[var(--text-secondary)]'}`}
              >
                {notificationsEnabled ? 'On' : 'Off'}
              </Button>
            </div>
          </div>
        </div>

        {/* System Settings */}
        <div className="mb-6">
          <h3 className="text-sm font-medium text-[var(--text-primary)] mb-3 flex items-center gap-2">
            <Zap size={16} />
            System
          </h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Database size={16} />
                <span className="text-sm">Auto-save</span>
              </div>
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => setAutoSave(!autoSave)}
                className={`p-2 ${autoSave ? 'text-accent' : 'text-[var(--text-secondary)]'}`}
              >
                {autoSave ? 'On' : 'Off'}
              </Button>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Shield size={16} />
                <span className="text-sm">Privacy Mode</span>
              </div>
              <Button variant="ghost" size="sm" className="p-2 text-[var(--text-secondary)]">
                Configure
              </Button>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Globe size={16} />
                <span className="text-sm">Language</span>
              </div>
              <Button variant="ghost" size="sm" className="p-2 text-[var(--text-secondary)]">
                English
              </Button>
            </div>
          </div>
        </div>

        {/* Shortcuts */}
        <div className="mb-6">
          <h3 className="text-sm font-medium text-[var(--text-primary)] mb-3 flex items-center gap-2">
            <Keyboard size={16} />
            Keyboard Shortcuts
          </h3>
          <div className="space-y-2">
            <Button 
              variant="ghost" 
              size="sm" 
              className="w-full justify-start text-left p-3 hover:bg-accent/10 hover:text-accent"
              onClick={() => {
                // This would open the KeyboardShortcuts modal
                const event = new CustomEvent('lukhas:shortcuts:show');
                document.dispatchEvent(event);
              }}
            >
              <div className="flex items-center gap-3">
                <Keyboard size={16} />
                <div>
                  <div className="text-sm font-medium">View all shortcuts</div>
                  <div className="text-xs text-[var(--text-secondary)]">Interactive shortcut guide</div>
                </div>
              </div>
              <div className="ml-auto">
                <code className="bg-[var(--surface)] px-2 py-1 rounded text-xs">⌘?</code>
              </div>
            </Button>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between pt-4 border-t border-[var(--border)]">
          <div className="text-xs text-[var(--text-secondary)]">
            LUKHΛS Studio v1.0.0
          </div>
          <div className="flex gap-2">
            <Button variant="ghost" size="sm" onClick={onClose}>
              Cancel
            </Button>
            <Button size="sm" onClick={onClose}>
              Save
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}