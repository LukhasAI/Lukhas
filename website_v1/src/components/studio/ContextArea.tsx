'use client';

import { useState, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/Button';
import { 
  Maximize2, 
  Minimize2,
  Palette,
  Play,
  BarChart3,
  Globe,
  Eye,
  Layers,
  Zap
} from 'lucide-react';

interface CanvasApp {
  id: string;
  title: string;
  kind: 'email' | 'calendar' | 'code' | 'models' | 'browser' | 'media';
}

interface ContextAreaProps {
  state: 'canvas' | 'preview' | 'player' | 'dashboard' | 'browser';
  onStateChange: (state: 'canvas' | 'preview' | 'player' | 'dashboard' | 'browser') => void;
  fullscreen: boolean;
  onFullscreenChange: (fullscreen: boolean) => void;
}

const contextStates = [
  {
    id: 'canvas' as const,
    label: 'Canvas',
    icon: Palette,
    description: 'Creative workspace and design canvas'
  },
  {
    id: 'preview' as const,
    label: 'Preview',
    icon: Eye,
    description: 'Preview and review content'
  },
  {
    id: 'player' as const,
    label: 'Player',
    icon: Play,
    description: 'Media player and content viewer'
  },
  {
    id: 'dashboard' as const,
    label: 'Dashboard',
    icon: BarChart3,
    description: 'Analytics and overview dashboard'
  },
  {
    id: 'browser' as const,
    label: 'Browser',
    icon: Globe,
    description: 'Web browser and research tool'
  }
];

export default function ContextArea({ 
  state, 
  onStateChange, 
  fullscreen, 
  onFullscreenChange 
}: ContextAreaProps) {
  const [isHovering, setIsHovering] = useState(false);
  const [browserUrl, setBrowserUrl] = useState('lukhas.ai');
  const [dwellTimer, setDwellTimer] = useState<NodeJS.Timeout | null>(null);
  const [canvases, setCanvases] = useState<CanvasApp[]>([]);
  const [viewMode, setViewMode] = useState<'carousel' | 'grid'>('carousel');
  const [activeIndex, setActiveIndex] = useState(0);
  const [isTyping, setIsTyping] = useState(false);
  const [showCanvas, setShowCanvas] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.code === 'Space' && e.target === document.body) {
        e.preventDefault();
        onFullscreenChange(!fullscreen);
      }
    };

    // Listen for typing events from chat
    const handleTypingStart = () => {
      setIsTyping(true);
      if (state === 'canvas') {
        setShowCanvas(true);
      }
    };

    const handleTypingStop = () => {
      setIsTyping(false);
      // Keep canvas visible for a bit after typing stops
      setTimeout(() => setShowCanvas(false), 2000);
    };

    // PATCH: handle lucas:navigate for browser mock
    const handleNavigate = (e: Event) => {
      const url = (e as CustomEvent).detail?.url as string | undefined;
      if (url) setBrowserUrl(url);
    };

    document.addEventListener('keydown', handleKeyPress);
    document.addEventListener('lucas:typing:start', handleTypingStart);
    document.addEventListener('lucas:typing:stop', handleTypingStop);
    document.addEventListener('lucas:navigate', handleNavigate as EventListener);
    
    return () => {
      document.removeEventListener('keydown', handleKeyPress);
      document.removeEventListener('lucas:typing:start', handleTypingStart);
      document.removeEventListener('lucas:typing:stop', handleTypingStop);
      document.removeEventListener('lucas:navigate', handleNavigate as EventListener);
    };
  }, [fullscreen, onFullscreenChange, state]);

  // Seed canvas apps when canvas becomes visible due to typing
  useEffect(() => {
    if (state === 'canvas' && showCanvas && canvases.length === 0) {
      setCanvases([
        { id: 'email',    title: 'Email',      kind: 'email' },
        { id: 'calendar', title: 'Calendar',   kind: 'calendar' },
        { id: 'code',     title: 'Code',       kind: 'code' },
        { id: 'models',   title: 'AI Models',  kind: 'models' },
      ]);
    }
  }, [state, showCanvas, canvases.length]);

  const handleCenterHover = (hovering: boolean) => {
    setIsHovering(hovering);
    
    if (dwellTimer) {
      clearTimeout(dwellTimer);
      setDwellTimer(null);
    }

    if (hovering && !fullscreen) {
      const timer = setTimeout(() => {
        // Auto-hide chrome after 500ms dwell
        // This would trigger UI chrome hiding in a real implementation
      }, 500);
      setDwellTimer(timer);
    }
  };

  // Handle swipe/trackpad gestures for carousel
  useEffect(() => {
    if (!containerRef.current || viewMode !== 'carousel' || canvases.length <= 1) return;

    let startX = 0;
    let startY = 0;
    let isScrolling = false;

    const handleTouchStart = (e: TouchEvent) => {
      startX = e.touches[0].clientX;
      startY = e.touches[0].clientY;
      isScrolling = false;
    };

    const handleTouchMove = (e: TouchEvent) => {
      if (!startX || !startY) return;

      const deltaX = e.touches[0].clientX - startX;
      const deltaY = e.touches[0].clientY - startY;

      if (!isScrolling) {
        isScrolling = Math.abs(deltaX) > Math.abs(deltaY);
      }

      if (isScrolling && Math.abs(deltaX) > 50) {
        e.preventDefault();
      }
    };

    const handleTouchEnd = (e: TouchEvent) => {
      if (!startX || !startY) return;

      const deltaX = e.changedTouches[0].clientX - startX;
      const deltaY = e.changedTouches[0].clientY - startY;

      if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 50) {
        if (deltaX > 0) {
          // Swipe right - previous
          setActiveIndex(prev => prev > 0 ? prev - 1 : canvases.length - 1);
        } else {
          // Swipe left - next
          setActiveIndex(prev => prev < canvases.length - 1 ? prev + 1 : 0);
        }
      }

      startX = 0;
      startY = 0;
      isScrolling = false;
    };

    const handleWheel = (e: WheelEvent) => {
      // Only handle horizontal scroll or shift+vertical scroll
      if (Math.abs(e.deltaX) > Math.abs(e.deltaY) || e.shiftKey) {
        e.preventDefault();
        
        if (e.deltaX > 10 || (e.shiftKey && e.deltaY > 10)) {
          // Scroll right - next
          setActiveIndex(prev => prev < canvases.length - 1 ? prev + 1 : 0);
        } else if (e.deltaX < -10 || (e.shiftKey && e.deltaY < -10)) {
          // Scroll left - previous
          setActiveIndex(prev => prev > 0 ? prev - 1 : canvases.length - 1);
        }
      }
    };

    const container = containerRef.current;
    container.addEventListener('touchstart', handleTouchStart, { passive: false });
    container.addEventListener('touchmove', handleTouchMove, { passive: false });
    container.addEventListener('touchend', handleTouchEnd, { passive: false });
    container.addEventListener('wheel', handleWheel, { passive: false });

    return () => {
      container.removeEventListener('touchstart', handleTouchStart);
      container.removeEventListener('touchmove', handleTouchMove);
      container.removeEventListener('touchend', handleTouchEnd);
      container.removeEventListener('wheel', handleWheel);
    };
  }, [viewMode, canvases.length]);

  const currentState = contextStates.find(s => s.id === state);
  const StateIcon = currentState?.icon || Palette;

  return (
    <div 
      ref={containerRef}
      className="bg-[var(--background)] flex flex-col relative"
      style={{ gridArea: 'context' }}
      onMouseEnter={() => handleCenterHover(true)}
      onMouseLeave={() => handleCenterHover(false)}
    >
      {/* Context Header - Removed */}
      {false && (
        <div className="flex items-center justify-between p-4 border-b border-[var(--border)] bg-[var(--surface)]/22">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <StateIcon size={18} className="text-accent" />
              <span className="font-medium text-[var(--text-primary)]">
                {currentState?.label}
              </span>
            </div>
            
            {/* Context State Switcher */}
            {false && (
              <div className="flex gap-1 bg-[var(--surface)] p-1 rounded-lg">
                {contextStates.map(({ id, icon: Icon, label }) => (
                  <button
                    key={id}
                    onClick={() => onStateChange(id)}
                    className={`
                      p-2 rounded-md transition-all duration-200 relative group
                      ${state === id 
                        ? 'bg-accent text-white' 
                        : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--surface)]'
                      }
                    `}
                  >
                    <Icon size={14} />
                    
                    {/* Tooltip */}
                    <div className="absolute bottom-full mb-2 left-1/2 transform -translate-x-1/2 px-2 py-1 bg-[var(--surface)] border border-[var(--border)] rounded-md text-xs whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity z-50">
                      {label}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="flex items-center gap-2">
            {/* View mode toggles (canvas only when panes exist) */}
            {state === 'canvas' && canvases.length > 0 && (
              <div className="flex items-center gap-1 mr-1">
                <Button variant="ghost" size="sm" className="p-1" onClick={() => setViewMode('carousel')} aria-label="Carousel View">C</Button>
                <Button variant="ghost" size="sm" className="p-1" onClick={() => setViewMode('grid')} aria-label="Grid View">G</Button>
              </div>
            )}
            
            {/* Fullscreen Toggle */}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onFullscreenChange(!fullscreen)}
              className="p-2 hover:bg-[var(--surface)]"
            >
              {fullscreen ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
            </Button>
          </div>
        </div>
      )}

      {/* Context Content */}
      <div className="flex-1 relative overflow-hidden">
        {state === 'canvas' && (
          <div className={`h-full relative transition-all duration-500 ease-out ${
            showCanvas ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
          }`}>
            {/* Only show canvas when typing or canvas is active */}
            {!showCanvas && <div className="h-full" />}

            {/* Carousel view: one active pane centered with dots */}
            {showCanvas && canvases.length > 0 && viewMode === 'carousel' && (
              <div className="h-full flex flex-col">
                <div className="flex-1 flex items-center justify-center">
                  <div className="w-[92%] h-[92%] rounded-lg border border-[var(--border)] bg-[var(--surface)]/22" role="group" aria-label="Active Canvas">
                    <div className="h-full w-full flex items-center justify-center text-[var(--text-secondary)]">
                      {canvases[activeIndex]?.title || 'Canvas'}
                    </div>
                  </div>
                </div>
                <div className="flex items-center justify-center gap-2 pb-3">
                  {canvases.map((c, i) => (
                    <button
                      key={c.id}
                      onClick={() => setActiveIndex(i)}
                      className={`w-2.5 h-2.5 rounded-full border border-[var(--border)] ${i === activeIndex ? 'bg-accent' : 'bg-[var(--surface)]'}`}
                      aria-label={`Show ${c.title}`}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Grid view: up to four panes visible simultaneously */}
            {showCanvas && canvases.length > 0 && viewMode === 'grid' && (
              <div className="h-full grid grid-cols-2 grid-rows-2 gap-3 p-3">
                {canvases.slice(0, 4).map((c) => (
                  <div key={c.id} className="rounded-lg border border-[var(--border)] bg-[var(--surface)]/22 flex items-center justify-center text-[var(--text-secondary)]">
                    {c.title}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {state === 'preview' && (
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <Eye size={48} className="mx-auto mb-4 text-[var(--text-secondary)]" />
              <h3 className="text-xl font-medium text-[var(--text-primary)] mb-2">
                Preview Mode
              </h3>
              <p className="text-[var(--text-secondary)]">
                Preview and review your content in real-time
              </p>
            </div>
          </div>
        )}

        {state === 'player' && (
          <div className="h-full flex items-center justify-center bg-black/20">
            <div className="text-center">
              <Play size={48} className="mx-auto mb-4 text-[var(--text-secondary)]" />
              <h3 className="text-xl font-medium text-[var(--text-primary)] mb-2">
                Media Player
              </h3>
              <p className="text-[var(--text-secondary)]">
                Play and interact with media content
              </p>
            </div>
          </div>
        )}

        {state === 'dashboard' && (
          <div className="h-full p-6">
            <div className="grid grid-cols-2 gap-4 h-full">
              <div className="bg-[var(--surface)]/22 rounded-lg p-4 border border-[var(--border)]">
                <h4 className="font-medium text-[var(--text-primary)] mb-2">Usage</h4>
                <div className="text-2xl font-bold text-accent mb-1">2,341</div>
                <div className="text-xs text-[var(--text-secondary)]">requests today</div>
              </div>
              <div className="bg-[var(--surface)]/22 rounded-lg p-4 border border-[var(--border)]">
                <h4 className="font-medium text-[var(--text-primary)] mb-2">Models</h4>
                <div className="text-2xl font-bold text-accent mb-1">4</div>
                <div className="text-xs text-[var(--text-secondary)]">active providers</div>
              </div>
              <div className="bg-[var(--surface)]/22 rounded-lg p-4 border border-[var(--border)]">
                <h4 className="font-medium text-[var(--text-primary)] mb-2">Files</h4>
                <div className="text-2xl font-bold text-accent mb-1">127</div>
                <div className="text-xs text-[var(--text-secondary)]">in workspace</div>
              </div>
              <div className="bg-[var(--surface)]/22 rounded-lg p-4 border border-[var(--border)]">
                <h4 className="font-medium text-[var(--text-primary)] mb-2">Status</h4>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span className="text-sm text-[var(--text-primary)]">All Systems</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {state === 'browser' && (
          <div className="h-full flex flex-col bg-[var(--surface)]/20">
            <div className="p-3 border-b border-[var(--border)] bg-[var(--surface)]/50">
              <div className="flex items-center gap-2">
                <div className="flex gap-1">
                  <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                  <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                </div>
                <div className="flex-1 bg-[var(--surface)] rounded-full px-3 py-1 text-sm text-[var(--text-secondary)]">
                  {browserUrl}
                </div>
              </div>
            </div>
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <Globe size={48} className="mx-auto mb-4 text-[var(--text-secondary)]" />
                <h3 className="text-xl font-medium text-[var(--text-primary)] mb-2">
                  Web Browser
                </h3>
                <p className="text-[var(--text-secondary)]">
                  Browse the web and research information
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Fullscreen indicator */}
        {fullscreen && (
          <div className="absolute top-4 right-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onFullscreenChange(false)}
              className="bg-black/20 backdrop-blur-sm hover:bg-black/30"
            >
              <Minimize2 size={16} />
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}