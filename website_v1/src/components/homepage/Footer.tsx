'use client';

import { FOOTER_LINKS, SOCIAL_LINKS } from '@/lib/constants';
import { ExternalLink, Instagram, MessageCircle } from 'lucide-react';

const socialIcons = {
  'Instagram': Instagram,
  'X': MessageCircle, // Using MessageCircle as placeholder for X
  'Discord': MessageCircle,
  'WhatsApp': MessageCircle,
};

export default function Footer() {
  return (
    <footer className="border-t border-[var(--border)] bg-[var(--surface)]/30 backdrop-blur-sm">
      <div className="container py-8">
        <div className="flex flex-col lg:flex-row justify-between items-center gap-6">
          {/* Brand */}
          <div className="flex items-center">
            <div className="text-h3 font-semibold text-[var(--text-primary)]">
              Lucas
            </div>
            <span className="ml-3 text-small text-[var(--text-secondary)]">
              © Lucas
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
              const Icon = socialIcons[social.name as keyof typeof socialIcons] || MessageCircle;
              
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
            Building the unified AI workspace for everyone
          </p>
        </div>
      </div>
    </footer>
  );
}