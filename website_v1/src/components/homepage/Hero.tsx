'use client';

import { Button } from '@/components/ui/Button';

export default function Hero() {
  return (
    <section className="relative min-h-[90vh] flex items-center justify-center bg-gradient-to-br from-[var(--background)] via-[var(--surface)] to-[var(--background)] overflow-hidden">
      {/* Background pattern */}
      <div className="absolute inset-0 bg-dots" />
      <div className="absolute inset-0 opacity-10 bg-[radial-gradient(circle_at_center,_var(--accent)_0px,_transparent_50%)]" />
      
      <div className="container relative z-10 text-center animate-fade-in">
        <h1 className="text-display font-semibold mb-6 text-[var(--text-primary)] leading-tight">
          Exploring
          <br />
          <span className="bg-gradient-to-r from-[var(--gradient-start)] to-[var(--gradient-end)] bg-clip-text text-transparent">
            Conscious AI
          </span>
        </h1>
        
        <p className="text-h4 text-[var(--text-secondary)] mb-8 max-w-3xl mx-auto font-normal leading-relaxed">
          LUKHAS AI explores the intersection of consciousness and computation—
          <br className="hidden sm:block" />
          developing systems that aim to be more adaptive and aware.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <Button 
            href="/studio"
            size="lg"
            className="px-8 py-4 text-lg bg-gradient-to-r from-[var(--gradient-start)] to-[var(--gradient-end)] hover:from-[var(--accent-hover)] hover:to-[var(--gradient-end)] border-0"
          >
            Experience LUKHAS Studio
          </Button>
          
          <Button 
            href="#about"
            variant="secondary"
            size="lg"
            className="px-8 py-4 text-lg border-[var(--accent)] text-[var(--accent)] hover:bg-[var(--accent)]/10"
          >
            Learn More
          </Button>
        </div>
      </div>
      
      {/* Decorative elements */}
      <div className="absolute top-20 left-10 w-32 h-32 bg-[var(--accent)]/10 rounded-full blur-2xl animate-pulse" />
      <div className="absolute bottom-20 right-10 w-48 h-48 bg-[var(--gradient-end)]/5 rounded-full blur-3xl" />
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-gradient-to-r from-[var(--accent)]/5 to-[var(--gradient-end)]/5 rounded-full blur-3xl opacity-30" />
    </section>
  );
}