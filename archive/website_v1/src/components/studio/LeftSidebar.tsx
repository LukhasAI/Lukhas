'use client';

import { Button } from '@/components/ui/Button';
import {
  Brain,
  Wrench,
  FileText,
  StickyNote,
  ChevronLeft,
  ChevronRight,
  SlidersHorizontal,
  Zap
} from 'lucide-react';
import { useState, useEffect } from 'react';
import SettingsModal from './Settings';
import KeyboardShortcuts from './KeyboardShortcuts';

interface LeftSidebarProps {
  collapsed: boolean;
  onToggle: () => void;
  contextState: string;
}

const widgets = [
  {
    id: 'models',
    label: 'Models',
    icon: Brain,
    badge: '4',
    description: 'AI Models & Providers'
  },
  {
    id: 'tools',
    label: 'Tools',
    icon: Wrench,
    badge: '12',
    description: 'Available Tools & Functions'
  },
  {
    id: 'files',
    label: 'Files',
    icon: FileText,
    badge: null,
    description: 'File Explorer & Management'
  },
  {
    id: 'notes',
    label: 'Notes',
    icon: StickyNote,
    badge: '3',
    description: 'Quick Notes & Scratchpad'
  }
];

export default function LeftSidebar({ collapsed, onToggle, contextState }: LeftSidebarProps) {
  const [activeWidget, setActiveWidget] = useState('models');
  const [showSettings, setShowSettings] = useState(false);
  const [showShortcuts, setShowShortcuts] = useState(false);
  const [focused, setFocused] = useState(false);

  // Global keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.metaKey || e.ctrlKey) {
        switch (e.key) {
          case ',':
            e.preventDefault();
            setShowSettings(true);
            break;
          case '?':
            e.preventDefault();
            setShowShortcuts(true);
            break;
        }
      }
    };

    const handleShortcutsEvent = () => {
      setShowShortcuts(true);
    };

    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('lukhas:shortcuts:show', handleShortcutsEvent);
    
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('lukhas:shortcuts:show', handleShortcutsEvent);
    };
  }, []);

  return (
    <div
      className={`relative flex flex-col transition-all duration-300 ease-in-out ${collapsed ? 'bg-transparent border-r-0' : 'bg-[var(--surface)]/50 border-r border-[var(--border)]'}`}
      style={{ gridArea: 'left' }}
    >
      {collapsed && (
        <button
          aria-label="Open left panel"
          onClick={onToggle}
          className="absolute top-1/2 -translate-y-1/2 right-[-6px] h-12 w-6 rounded-l-md bg-[var(--surface)]/60 border border-[var(--border)] hover:bg-[var(--surface)]/80 flex items-center justify-center"
        >
          <ChevronRight size={12} />
        </button>
      )}
      {collapsed && (
        <div className="pointer-events-none absolute top-0 right-0 h-full w-3 bg-gradient-to-l from-white/10 to-transparent" />
      )}
      {/* Header */}
      <div className="p-4 border-b border-[var(--border)] flex items-center justify-between">
        {!collapsed && (
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" className="ml-0 p-1" aria-label="Preferences" onClick={() => setShowSettings(true)}>
              <SlidersHorizontal size={16} />
            </Button>
            <span
              className="font-thin text-[17px] tracking-[0.35em] text-[var(--text-primary)] leading-none"
              style={{ 
                fontFamily: '"Helvetica Neue", Helvetica, Arial, ui-sans-serif, system-ui',
                fontWeight: '200'
              }}
            >
              LUKHΛS
            </span>
            {focused && (
              <Button variant="ghost" size="sm" className="p-1" aria-label="Back to menu" onClick={() => setFocused(false)}>
                <ChevronLeft size={14} />
              </Button>
            )}
          </div>
        )}
        
        <Button
          variant="ghost"
          size="sm"
          onClick={onToggle}
          className="p-1 hover:bg-[var(--surface)]"
        >
          {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </Button>
      </div>

      {/* Widget Navigation */}
      <div className="flex-1 overflow-hidden">
        <div className="p-2">
          {!focused && widgets.map((widget) => {
            const Icon = widget.icon;
            const isActive = activeWidget === widget.id;
            
            return (
              <button
                key={widget.id}
                onClick={() => { setActiveWidget(widget.id); setFocused(true); }}
                className={`
                  w-full flex items-center gap-3 p-3 rounded-lg transition-all duration-200
                  hover:bg-[var(--surface)] group relative
                  ${isActive ? 'bg-accent/10 text-accent border-l-2 border-accent' : 'text-[var(--text-secondary)]'}
                `}
              >
                <Icon size={18} className={isActive ? 'text-accent' : 'text-[var(--text-secondary)] group-hover:text-[var(--text-primary)]'} />
                
                {!collapsed && (
                  <>
                    <div className="flex-1 text-left">
                      <div className={`text-sm font-medium ${isActive ? 'text-accent' : 'text-[var(--text-primary)] group-hover:text-[var(--text-primary)]'}`}>
                        {widget.label}
                      </div>
                    </div>
                    
                    {widget.badge && (
                      <div className="bg-accent/20 text-accent text-xs px-2 py-0.5 rounded-full">
                        {widget.badge}
                      </div>
                    )}
                  </>
                )}
                
                {/* Tooltip for collapsed state */}
                {collapsed && (
                  <div className="absolute left-full ml-2 px-2 py-1 bg-[var(--surface)] border border-[var(--border)] rounded-md text-xs whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity z-50">
                    {widget.label}
                    {widget.badge && ` (${widget.badge})`}
                  </div>
                )}
              </button>
            );
          })}
        </div>

        {/* Widget Content Area */}
        {!collapsed && (
          <div className="flex-1 p-4 border-t border-[var(--border)] mt-2">
            
            {activeWidget === 'models' && (
              <div className="text-xs text-[var(--text-secondary)]">
                Model selection is shown in the footer. Use Preferences (⌘,) to change providers.
              </div>
            )}
            
            {activeWidget === 'tools' && (
              <div className="space-y-2">
                <div className="text-xs text-[var(--text-tertiary)] mb-2">Available Tools</div>
                {['Code Editor', 'Web Browser', 'File Manager', 'Terminal', 'Cloud', 'Wallet'].map((tool) => (
                  <div key={tool} className="flex items-center gap-2 p-2 hover:bg-[var(--surface)] rounded-md cursor-pointer">
                    <Zap size={14} className="text-[var(--text-secondary)]" />
                    <span className="text-sm">{tool}</span>
                  </div>
                ))}
              </div>
            )}
            
            {activeWidget === 'files' && (
              <div className="space-y-3">
                <div className="flex gap-2">
                  <input
                    type="text"
                    placeholder="Search files..."
                    className="flex-1 px-3 py-2 text-sm bg-[var(--background)] border border-[var(--border)] rounded-md"
                  />
                  <Button variant="secondary" size="sm" className="px-2">Upload</Button>
                </div>
                <div className="flex items-center gap-2 text-xs text-[var(--text-secondary)]">
                  <Button variant="ghost" size="sm" className="px-2 py-1 border border-[var(--border)] rounded-md">Compress</Button>
                  <Button variant="ghost" size="sm" className="px-2 py-1 border border-[var(--border)] rounded-md">Decompress</Button>
                  <label className="ml-1 flex items-center gap-1">
                    <input type="checkbox" className="accent-[var(--accent)]" />
                    <span>Use Lucas Folds (encrypted)</span>
                  </label>
                </div>
                <div className="text-xs text-[var(--text-tertiary)]">Recent Files</div>
                <div className="text-xs text-[var(--text-secondary)]">No files opened yet</div>
              </div>
            )}
            
            {activeWidget === 'notes' && (
              <div className="space-y-2">
                {['Quick Ideas', 'Product Todos', 'Meeting Notes'].map((title, idx) => (
                  <div key={title} className="p-2 bg-[var(--surface)] border border-[var(--border)] rounded-md flex items-center justify-between">
                    <div>
                      <div className="text-sm">{title}</div>
                      <div className="text-xs text-[var(--text-secondary)]">{idx === 0 ? '2 minutes ago' : 'Today'}</div>
                    </div>
                    <Button
                      variant="secondary"
                      size="sm"
                      className="px-2"
                      onClick={() => document.dispatchEvent(new CustomEvent('lucas:open-note', { detail: { title } }))}
                    >
                      Open in Canvas
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>


      {/* Modals */}
      <SettingsModal isOpen={showSettings} onClose={() => setShowSettings(false)} />
      <KeyboardShortcuts isOpen={showShortcuts} onClose={() => setShowShortcuts(false)} />
    </div>
  );
}