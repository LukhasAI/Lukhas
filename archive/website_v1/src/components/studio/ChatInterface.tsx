'use client';

import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { 
  Send,
  Paperclip,
  Code2,
  Mail,
  MessageSquare,
  FileText,
  Brain,
  Mic,
  MoreHorizontal,
  Sparkles,
  Globe,
  Play,
  BarChart3,
  Check
} from 'lucide-react';

interface ChatInterfaceProps {
  fullscreen: boolean;
  contextState: string;
}

const inputModes = [
  { id: 'chat', label: 'Chat', icon: MessageSquare, placeholder: 'Ask Lucas anything...' },
  { id: 'code', label: 'Code', icon: Code2, placeholder: 'Describe the code you want to write...' },
  { id: 'email', label: 'Email', icon: Mail, placeholder: 'Compose an email...' },
  { id: 'command', label: 'Command', icon: Sparkles, placeholder: 'Type a command or use / for shortcuts...' }
];

const quickActions = [
  { id: 'text', icon: MessageSquare, tooltip: 'Text' },
  { id: 'code', icon: Code2, tooltip: 'Write Code' },
  { id: 'email', icon: Mail, tooltip: 'Compose Email' },
  { id: 'file', icon: FileText, tooltip: 'Attach File' },
  { id: 'model', icon: Brain, tooltip: 'Switch Model' }
];

export default function ChatInterface({ fullscreen, contextState }: ChatInterfaceProps) {
  const [message, setMessage] = useState('');
  const [mode, setMode] = useState<'chat' | 'code' | 'email' | 'command'>('chat');
  const [isExpanded, setIsExpanded] = useState(false);
  const [typingTimeout, setTypingTimeout] = useState<NodeJS.Timeout | null>(null);
  const [justSent, setJustSent] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [messages, setMessages] = useState<Array<{
    id: number;
    type: 'system' | 'user' | 'assistant';
    content: string;
    timestamp: Date;
  }>>([
    {
      id: 1,
      type: 'system' as const,
      content: 'Welcome to Lucas Studio! I\'m here to help you with anything you need.',
      timestamp: new Date()
    }
  ]);
  // --- PATCH: sending state and URL detection
  const [sending, setSending] = useState(false);
  const isUrl = /^((https?:\/\/)|www\.)\S+$/i.test(message.trim());

  const currentMode = inputModes.find(m => m.id === mode) || inputModes[0];

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [message]);

  // Typing detection and broadcast
  const handleTypingChange = (value: string) => {
    setMessage(value);
    
    // Clear existing timeout
    if (typingTimeout) {
      clearTimeout(typingTimeout);
    }
    
    // Broadcast typing start
    document.dispatchEvent(new CustomEvent('lucas:typing:start'));
    
    // Set timeout to stop typing after 1 second of inactivity
    const timeout = setTimeout(() => {
      document.dispatchEvent(new CustomEvent('lucas:typing:stop'));
    }, 1000);
    
    setTypingTimeout(timeout);
  };

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (typingTimeout) {
        clearTimeout(typingTimeout);
      }
    };
  }, [typingTimeout]);

  // PATCH: new handleSubmit for play/sending/check and URL dispatch
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;

    setSending(true);

    const userMessage = {
      id: messages.length + 1,
      type: 'user' as const,
      content: message,
      timestamp: new Date()
    };

    // Dispatch URL navigate event if it looks like a URL
    if (isUrl) {
      document.dispatchEvent(new CustomEvent('lucas:navigate', { detail: { url: message.trim() } }));
    }

    const aiMessage = {
      id: messages.length + 2,
      type: 'assistant' as const,
      content: `I understand you want to ${isUrl ? 'open a website' : mode === 'code' ? 'write code' : mode === 'email' ? 'compose an email' : mode === 'command' ? 'run a command' : 'chat'}. How can I help with that?`,
      timestamp: new Date()
    };

    setMessages([...messages, userMessage, aiMessage]);
    setMessage('');

    setTimeout(() => {
      setSending(false);
      setJustSent(true);
      setTimeout(() => setJustSent(false), 900);
    }, 600);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as any);
    }
  };

  if (fullscreen) {
    return null; // Hide in fullscreen mode
  }

  return (
    <div 
      className={`bg-transparent border-t-0 flex flex-col transition-all duration-300 ease-in-out ${isExpanded ? 'h-60' : 'h-auto'} md:relative md:bottom-0 sm:fixed sm:bottom-0 sm:left-0 sm:right-0 sm:z-50 sm:pb-safe`}
      style={{ gridArea: 'chat' }}
    >
      {/* Chat History (when expanded) */}
      {isExpanded && (
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`
                  max-w-[80%] p-3 rounded-lg text-sm
                  ${
                    msg.type === 'user'
                      ? 'bg-accent text-white'
                      : msg.type === 'system'
                      ? 'bg-[var(--surface)] border border-[var(--border)] text-[var(--text-secondary)]'
                      // PATCH: darker bubble for assistant
                      : 'bg-[var(--surface)] border border-[var(--border)] text-[var(--text-primary)]'
                  }
                `}
              >
                {msg.content}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Input Area */}
      <div className="px-4 py-2">
        {/* Mode Switcher removed */}

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="flex items-end">
          <div className="flex-1 relative">
            {/* PATCH: quick icon rail opacity on URL */}
            <div className={`absolute left-2 bottom-3 flex items-center gap-0.5 z-10 ${isUrl ? 'opacity-70' : 'opacity-100'}`}>
              <Button 
                variant="ghost" 
                size="sm" 
                className={`px-1 py-1 h-auto ${mode === 'chat' ? 'bg-accent/20 text-accent' : ''}`} 
                aria-label="Text" 
                onClick={() => setMode('chat')}
              >
                <MessageSquare size={13} />
              </Button>
              <Button 
                variant="ghost" 
                size="sm" 
                className={`px-1 py-1 h-auto ${mode === 'code' ? 'bg-accent/20 text-accent' : ''}`} 
                aria-label="Code" 
                onClick={() => setMode('code')}
              >
                <Code2 size={13} />
              </Button>
              <Button 
                variant="ghost" 
                size="sm" 
                className={`px-1 py-1 h-auto ${mode === 'email' ? 'bg-accent/20 text-accent' : ''}`} 
                aria-label="Email" 
                onClick={() => setMode('email')}
              >
                <Mail size={13} />
              </Button>
              {/* PATCH: Globe quick icon */}
              <Button 
                variant="ghost" 
                size="sm" 
                className={`px-1 py-1 h-auto ${mode === 'command' && isUrl ? 'bg-accent/20 text-accent' : ''}`} 
                aria-label="Browser"
                onClick={() => setMode('command')}
              >
                <Globe size={13} />
              </Button>
              <Button 
                variant="ghost" 
                size="sm" 
                className={`px-1 py-1 h-auto ${mode === 'command' && !isUrl ? 'bg-accent/20 text-accent' : ''}`} 
                aria-label="Command" 
                onClick={() => setMode('command')}
              >
                <Sparkles size={13} />
              </Button>
            </div>
            {/* PATCH: textarea className for compact URL input */}
            <textarea
              ref={textareaRef}
              value={message}
              onChange={(e) => handleTypingChange(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={currentMode.placeholder}
              className={`w-full bg-[var(--surface)]/30 border border-[var(--border)] rounded-[14px] pl-16 pr-28 py-2 ${isUrl ? 'min-h-[44px] pb-8' : 'min-h-[56px] pb-12'} text-[var(--text-primary)] placeholder-[var(--text-secondary)] resize-none focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-accent max-h-[120px] shadow-subtle backdrop-blur-sm`}
              rows={2}
            />
            {/* PATCH: right icon rail baseline alignment */}
            <div className="absolute right-3 bottom-3 flex items-center gap-1 z-10">
              <Button variant="ghost" size="sm" className="p-1 h-auto" aria-label="Attach">
                <Paperclip size={13} />
              </Button>
              <Button variant="ghost" size="sm" className="p-1 h-auto" aria-label="Voice">
                <Mic size={13} />
              </Button>
              {/* PATCH: Send icon always visible, play/sending/check state */}
              <Button 
                type="submit" 
                disabled={!message.trim() && !justSent}
                className="flex items-center justify-center h-7 w-7 rounded-[10px] bg-accent hover:bg-accent/90 disabled:opacity-70 disabled:cursor-not-allowed text-white"
                aria-label="Send"
              >
                {sending ? <Play size={12} className="animate-pulse" /> : justSent ? <Check size={12} className="text-white" /> : <Play size={12} className="text-white" />}
              </Button>
            </div>
          </div>
        </form>

      </div>
    </div>
  );
}