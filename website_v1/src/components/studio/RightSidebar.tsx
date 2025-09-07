'use client';

import { Button } from '@/components/ui/Button';
import { 
  Mail, 
  Inbox, 
  MessageSquare, 
  Calendar,
  ChevronLeft,
  ChevronRight,
  Clock,
  Users,
  Settings
} from 'lucide-react';
import { useState } from 'react';

interface RightSidebarProps {
  collapsed: boolean;
  onToggle: () => void;
  contextState: string;
}

const widgets = [
  {
    id: 'email',
    label: 'Email',
    icon: Mail,
    badge: '12',
    description: 'Email management and composition'
  },
  {
    id: 'inbox',
    label: 'Inbox',
    icon: Inbox,
    badge: '3',
    description: 'Unified inbox for all communications'
  },
  {
    id: 'chat_history',
    label: 'Chat History',
    icon: MessageSquare,
    badge: null,
    description: 'Previous conversations and threads'
  },
  {
    id: 'calendar',
    label: 'Calendar',
    icon: Calendar,
    badge: '2',
    description: 'Schedule and upcoming events'
  }
];

export default function RightSidebar({ collapsed, onToggle, contextState }: RightSidebarProps) {
  const [activeWidget, setActiveWidget] = useState('inbox');
  const activeIdx = widgets.findIndex(w => w.id === activeWidget);

  return (
    <div
      className={`relative flex flex-col transition-all duration-300 ease-in-out ${collapsed ? 'bg-transparent border-l-0' : 'bg-[var(--surface)]/50 border-l border-[var(--border)]'}`}
      style={{ gridArea: 'right' }}
    >
      {collapsed && (
        <button
          aria-label="Open right panel"
          onClick={onToggle}
          className="absolute top-1/2 -translate-y-1/2 left-[-6px] h-12 w-6 rounded-r-md bg-[var(--surface)]/60 border border-[var(--border)] hover:bg-[var(--surface)]/80 flex items-center justify-center"
        >
          <ChevronLeft size={12} />
        </button>
      )}
      {collapsed && (
        <div className="pointer-events-none absolute top-0 left-0 h-full w-3 bg-gradient-to-r from-white/10 to-transparent" />
      )}
      {/* Header */}
      <div className="p-2 border-b border-[var(--border)] flex items-center justify-start">
        <Button variant="ghost" size="sm" onClick={onToggle} className="p-1 hover:bg-[var(--surface)]">
          {collapsed ? <ChevronLeft size={16} /> : <ChevronRight size={16} />}
        </Button>
      </div>

      {/* Widget Navigation */}
      <div className="flex-1 overflow-hidden">
        <div className="p-2">
          {!collapsed && (
            <div className="mb-2 relative overflow-x-auto select-none">
              <div className="flex rounded-full bg-[var(--surface)]/30 border border-[var(--border)] p-1 min-w-max">
                {widgets.map((w) => {
                  const Icon = w.icon;
                  const isActive = activeWidget === w.id;
                  return (
                    <button
                      key={w.id}
                      onClick={() => setActiveWidget(w.id)}
                      className={`relative flex-1 flex-[0_0_auto] h-8 px-2 rounded-full text-xs flex items-center justify-center gap-1 transition-colors select-none ${isActive ? 'text-[var(--text-primary)] bg-accent/15' : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--surface)]/30'}`}
                      style={{ zIndex: 1 }}
                    >
                      <Icon size={12} className={isActive ? 'text-accent' : 'text-[var(--text-secondary)]'} />
                      <span className="truncate hidden md:inline">{w.label}</span>
                      {w.badge && <span className="ml-1 text-[10px] px-1.5 py-0.5 rounded-full bg-accent/20 text-accent">{w.badge}</span>}
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Widget Content Area */}
        {!collapsed && (
          <div className="flex-1 p-4 border-t border-[var(--border)] mt-2">
            <div className="text-xs text-[var(--text-secondary)] mb-3 uppercase tracking-wider">
              {widgets.find(w => w.id === activeWidget)?.label}
            </div>
            
            {activeWidget === 'email' && (
              <div className="space-y-3">
                <div className="p-3 bg-accent/5 border border-accent/20 rounded-md">
                  <div className="flex items-start justify-between mb-2">
                    <div className="w-8 h-8 bg-accent/20 rounded-full flex items-center justify-center">
                      <span className="text-xs font-medium text-accent">JD</span>
                    </div>
                    <div className="text-xs text-[var(--text-secondary)]">2m ago</div>
                  </div>
                  <div className="text-sm font-medium mb-1">Weekly Report</div>
                  <div className="text-xs text-[var(--text-secondary)] line-clamp-2">
                    Here's the summary of this week's progress and key metrics...
                  </div>
                </div>
                
                <div className="p-3 bg-[var(--surface)] border border-[var(--border)] rounded-md">
                  <div className="flex items-start justify-between mb-2">
                    <div className="w-8 h-8 bg-orange-500/20 rounded-full flex items-center justify-center">
                      <span className="text-xs font-medium text-orange-500">AI</span>
                    </div>
                    <div className="text-xs text-[var(--text-secondary)]">1h ago</div>
                  </div>
                  <div className="text-sm font-medium mb-1">System Update</div>
                  <div className="text-xs text-[var(--text-secondary)] line-clamp-2">
                    New features have been deployed to your workspace...
                  </div>
                </div>
              </div>
            )}
            
            {activeWidget === 'inbox' && (
              <div className="space-y-3">
                <div className="p-3 bg-accent/5 border border-accent/20 rounded-md">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-2 h-2 bg-accent rounded-full"></div>
                    <span className="text-sm font-medium">New Messages</span>
                  </div>
                  <div className="text-xs text-[var(--text-secondary)]">
                    3 unread from various channels
                  </div>
                </div>
                
                <div className="space-y-2">
                  <div className="flex items-center gap-2 p-2 hover:bg-[var(--surface)] rounded-md cursor-pointer">
                    <Mail size={14} className="text-[var(--text-secondary)]" />
                    <div className="flex-1 min-w-0">
                      <div className="text-sm truncate">Team standup notes</div>
                      <div className="text-xs text-[var(--text-secondary)]">5 min ago</div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2 p-2 hover:bg-[var(--surface)] rounded-md cursor-pointer">
                    <MessageSquare size={14} className="text-[var(--text-secondary)]" />
                    <div className="flex-1 min-w-0">
                      <div className="text-sm truncate">Lucas feedback</div>
                      <div className="text-xs text-[var(--text-secondary)]">12 min ago</div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            {activeWidget === 'chat_history' && (
              <div className="space-y-2">
                <div className="text-xs text-[var(--text-tertiary)] mb-2">Recent Conversations</div>
                <div className="space-y-2">
                  <div className="p-2 bg-[var(--surface)] border border-[var(--border)] rounded-md">
                    <div className="text-sm mb-1">Project Planning</div>
                    <div className="text-xs text-[var(--text-secondary)]">Today, 2:30 PM</div>
                  </div>
                  <div className="p-2 bg-[var(--surface)] border border-[var(--border)] rounded-md">
                    <div className="text-sm mb-1">Code Review</div>
                    <div className="text-xs text-[var(--text-secondary)]">Yesterday, 4:15 PM</div>
                  </div>
                </div>
              </div>
            )}
            
            {activeWidget === 'calendar' && (
              <div className="space-y-3">
                <div className="p-3 bg-accent/5 border border-accent/20 rounded-md">
                  <div className="flex items-center gap-2 mb-2">
                    <Clock size={14} className="text-accent" />
                    <span className="text-sm font-medium">Next Meeting</span>
                  </div>
                  <div className="text-sm mb-1">Team Sync</div>
                  <div className="text-xs text-[var(--text-secondary)]">Today, 3:00 PM</div>
                </div>
                
                <div className="space-y-2">
                  <div className="text-xs text-[var(--text-tertiary)] mb-2">Upcoming</div>
                  <div className="p-2 bg-[var(--surface)] border border-[var(--border)] rounded-md">
                    <div className="text-sm mb-1">Product Review</div>
                    <div className="text-xs text-[var(--text-secondary)]">Tomorrow, 10:00 AM</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Footer spacer removed: settings moved to Left header */}
    </div>
  );
}