'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { 
  Crown,
  Sparkles,
  Zap,
  Star,
  Hexagon,
  Triangle,
  Circle,
  Square,
  Diamond,
  X,
  Copy,
  Download,
  Share,
  Palette,
  Type,
  Image,
  Layout,
  Eye
} from 'lucide-react';

interface BrandingProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function Branding({ isOpen, onClose }: BrandingProps) {
  const [selectedLogo, setSelectedLogo] = useState('lambda');
  const [selectedVariant, setSelectedVariant] = useState('primary');

  if (!isOpen) return null;

  const logos = [
    { id: 'lambda', name: 'LUKHΛS', symbol: 'Λ', description: 'Classic lambda symbol' },
    { id: 'crown', name: 'LUKHAS', symbol: '👑', description: 'Royal crown variant' },
    { id: 'diamond', name: 'LUKHAS', symbol: '◇', description: 'Diamond crystal' },
    { id: 'spark', name: 'LUKHAS', symbol: '✦', description: 'Consciousness spark' }
  ];

  const colorVariants = [
    { id: 'primary', name: 'Primary', color: '#4F8BFF', bg: 'bg-[#4F8BFF]' },
    { id: 'white', name: 'White', color: '#FFFFFF', bg: 'bg-white border' },
    { id: 'dark', name: 'Dark', color: '#0B0B0F', bg: 'bg-[#0B0B0F]' },
    { id: 'gradient', name: 'Gradient', color: 'linear-gradient(45deg, #4F8BFF, #FF6B9D)', bg: 'bg-gradient-to-r from-[#4F8BFF] to-[#FF6B9D]' }
  ];

  const brandElements = [
    {
      category: 'Typography',
      icon: Type,
      items: [
        { name: 'Primary Font', value: 'Inter', usage: 'Headlines, UI text' },
        { name: 'Accent Font', value: 'SF Mono', usage: 'Code, technical text' }
      ]
    },
    {
      category: 'Colors',
      icon: Palette,
      items: [
        { name: 'Primary Blue', value: '#4F8BFF', usage: 'Primary actions, links' },
        { name: 'Background Dark', value: '#0B0B0F', usage: 'Main background' },
        { name: 'Surface', value: '#111216', usage: 'Cards, panels' },
        { name: 'Text Primary', value: '#FFFFFF', usage: 'Main text' }
      ]
    }
  ];

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center">
      <div className="bg-[var(--surface)] border border-[var(--border)] rounded-2xl p-6 w-[600px] max-h-[80vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <Crown size={20} className="text-accent" />
            <h2 className="text-xl font-semibold text-[var(--text-primary)]">Brand Identity</h2>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose} className="p-1">
            <X size={18} />
          </Button>
        </div>

        {/* Logo Variants */}
        <div className="mb-6">
          <h3 className="text-sm font-medium text-[var(--text-primary)] mb-4 flex items-center gap-2">
            <Image size={16} />
            Logo Variants
          </h3>
          
          {/* Logo Selection */}
          <div className="grid grid-cols-2 gap-3 mb-4">
            {logos.map((logo) => (
              <button
                key={logo.id}
                onClick={() => setSelectedLogo(logo.id)}
                className={`p-4 rounded-lg border-2 transition-all ${
                  selectedLogo === logo.id 
                    ? 'border-accent bg-accent/10' 
                    : 'border-[var(--border)] hover:border-accent/50'
                }`}
              >
                <div className="text-2xl mb-2">{logo.symbol}</div>
                <div className="font-semibold text-sm">{logo.name}</div>
                <div className="text-xs text-[var(--text-secondary)] mt-1">{logo.description}</div>
              </button>
            ))}
          </div>

          {/* Color Variants */}
          <div className="space-y-3">
            <label className="text-xs text-[var(--text-secondary)]">Color Variants</label>
            <div className="flex gap-2">
              {colorVariants.map((variant) => (
                <button
                  key={variant.id}
                  onClick={() => setSelectedVariant(variant.id)}
                  className={`px-3 py-2 rounded-md text-xs border transition-all ${
                    selectedVariant === variant.id
                      ? 'border-accent bg-accent/10 text-accent'
                      : 'border-[var(--border)] text-[var(--text-secondary)] hover:border-accent/50'
                  }`}
                >
                  <div className={`w-4 h-4 rounded-full ${variant.bg} mx-auto mb-1`}></div>
                  {variant.name}
                </button>
              ))}
            </div>
          </div>

          {/* Preview */}
          <div className="mt-4 p-4 bg-[var(--background)] rounded-lg border border-[var(--border)]">
            <div className="text-center">
              <div className="text-4xl mb-2">
                {logos.find(l => l.id === selectedLogo)?.symbol}
              </div>
              <div 
                className="text-2xl"
                style={{ 
                  fontFamily: '"Helvetica Neue", -apple-system, BlinkMacSystemFont, sans-serif',
                  fontWeight: '100',
                  letterSpacing: '0.05em',
                  color: selectedVariant === 'gradient' ? undefined : colorVariants.find(v => v.id === selectedVariant)?.color,
                  background: selectedVariant === 'gradient' ? colorVariants.find(v => v.id === selectedVariant)?.color : undefined,
                  WebkitBackgroundClip: selectedVariant === 'gradient' ? 'text' : undefined,
                  WebkitTextFillColor: selectedVariant === 'gradient' ? 'transparent' : undefined
                }}
              >
                {logos.find(l => l.id === selectedLogo)?.name}
              </div>
              <div 
                className="text-sm text-[var(--text-secondary)] mt-2"
                style={{ 
                  fontFamily: '"Helvetica Neue", -apple-system, BlinkMacSystemFont, sans-serif',
                  fontWeight: '100',
                  letterSpacing: '0.02em'
                }}
              >
                AI Consciousness Platform
              </div>
            </div>
          </div>
        </div>

        {/* Brand Elements */}
        <div className="mb-6">
          <h3 className="text-sm font-medium text-[var(--text-primary)] mb-4 flex items-center gap-2">
            <Layout size={16} />
            Brand System
          </h3>
          
          {brandElements.map((element) => {
            const Icon = element.icon;
            return (
              <div key={element.category} className="mb-4">
                <h4 className="text-xs font-medium text-[var(--text-secondary)] mb-2 flex items-center gap-2">
                  <Icon size={14} />
                  {element.category}
                </h4>
                <div className="space-y-2">
                  {element.items.map((item, index) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-[var(--surface)] rounded-md">
                      <div>
                        <div className="text-sm font-medium">{item.name}</div>
                        <div className="text-xs text-[var(--text-secondary)]">{item.usage}</div>
                      </div>
                      <div className="flex items-center gap-2">
                        {element.category === 'Colors' && (
                          <div 
                            className="w-4 h-4 rounded border border-[var(--border)]"
                            style={{ backgroundColor: item.value }}
                          ></div>
                        )}
                        <code className="text-xs bg-[var(--background)] px-2 py-1 rounded">
                          {item.value}
                        </code>
                        <Button variant="ghost" size="sm" className="p-1" aria-label="Copy">
                          <Copy size={12} />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>

        {/* Brand Guidelines */}
        <div className="mb-6">
          <h3 className="text-sm font-medium text-[var(--text-primary)] mb-3 flex items-center gap-2">
            <Eye size={16} />
            Usage Guidelines
          </h3>
          <div className="space-y-3 text-sm text-[var(--text-secondary)]">
            <div className="p-3 bg-accent/5 border border-accent/20 rounded-md">
              <div className="font-medium text-accent mb-1">Λ Symbol Usage</div>
              <div className="text-xs">Use Λ (lambda) only in display contexts: logos, wordmarks, headers. Use "Lukhas" in body text.</div>
            </div>
            <div className="p-3 bg-[var(--surface)] border border-[var(--border)] rounded-md">
              <div className="font-medium text-[var(--text-primary)] mb-1">Consciousness Terminology</div>
              <div className="text-xs">Always use "quantum-inspired" and "bio-inspired" rather than direct quantum/bio claims.</div>
            </div>
            <div className="p-3 bg-[var(--surface)] border border-[var(--border)] rounded-md">
              <div className="font-medium text-[var(--text-primary)] mb-1">Vendor Neutrality</div>
              <div className="text-xs">Use "uses [Provider] APIs" not "powered by [Provider]" for third-party integrations.</div>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between pt-4 border-t border-[var(--border)]">
          <div className="text-xs text-[var(--text-secondary)]">
            Brand Guidelines v1.0
          </div>
          <div className="flex gap-2">
            <Button variant="ghost" size="sm" className="flex items-center gap-2">
              <Download size={14} />
              Export
            </Button>
            <Button variant="ghost" size="sm" className="flex items-center gap-2">
              <Share size={14} />
              Share
            </Button>
            <Button size="sm" onClick={onClose}>
              Close
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}