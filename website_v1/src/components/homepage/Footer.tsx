'use client';

import { FOOTER_LINKS, SOCIAL_LINKS } from '@/lib/constants';
import { ExternalLink, Instagram, Github } from 'lucide-react';

// Custom X (Twitter) icon component
const XIcon = ({ size = 16 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
  </svg>
);

const socialIcons = {
  'Instagram': Instagram,
  'X': XIcon,
  'GitHub': Github,
};

export default function Footer() {
  return (
    <footer className="border-t border-[var(--border)] bg-[var(--surface)]/30 backdrop-blur-sm">
      <div className="container py-8">
        <div className="flex flex-col lg:flex-row justify-between items-center gap-6">
          {/* Brand */}
          <div className="flex items-center">
            <div className="text-h3 text-[var(--text-primary)]" style={{ fontFamily: 'Helvetica Neue, -apple-system, BlinkMacSystemFont, sans-serif', fontWeight: 100 }}>
              LUKHΛS ΛI
            </div>
            <span className="ml-3 text-small text-[var(--text-secondary)]" style={{ fontFamily: 'Helvetica Neue, -apple-system, BlinkMacSystemFont, sans-serif', fontWeight: 100 }}>
              © LUKHΛS ΛI
            </span>
          </div>
          
          {/* Navigation Links */}
          <nav className="flex flex-wrap justify-center gap-8">
            {FOOTER_LINKS.map((link) => {
              const isExternal = link.href.startsWith('http');
              
              return (
                <a
                  key={link.label}
                  href={link.href}
                  target={isExternal ? '_blank' : '_self'}
                  rel={isExternal ? 'noopener noreferrer' : undefined}
                  className="flex items-center gap-1 text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors duration-200"
                >
                  {link.label}
                  {isExternal && <ExternalLink size={14} />}
                </a>
              );
            })}
          </nav>
          
          {/* Social Links */}
          <div className="flex items-center gap-4">
            {SOCIAL_LINKS.map((social) => {
              const Icon = socialIcons[social.name as keyof typeof socialIcons] || XIcon;
              
              return (
                <a
                  key={social.name}
                  href={social.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-2 rounded-lg bg-[var(--surface)] border border-[var(--border)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:border-accent/50 transition-all duration-200"
                  title={social.name}
                >
                  <Icon size={16} />
                </a>
              );
            })}
          </div>
        </div>
        
        {/* Mobile stacked layout */}
        <div className="lg:hidden mt-6 pt-6 border-t border-[var(--border)] text-center">
          <p className="text-small text-[var(--text-secondary)]">
            Agent coordination hub with multi-AI orchestration and consciousness patterns
          </p>
        </div>
      </div>
    </footer>
  );
}