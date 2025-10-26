'use client';

import Link from 'next/link';
import { VISION_POINTS } from '@/lib/constants';
import { CheckCircle, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/Button';

export default function Vision() {
  return (
    <section className="section-padding bg-[var(--surface)]/30">
      <div className="container">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-h2 font-semibold text-[var(--text-primary)] mb-4">
              Vision
            </h2>
            <p className="text-body text-[var(--text-secondary)] max-w-2xl mx-auto">
              We're building the future of human-AI collaboration, 
              where technology adapts to you, not the other way around.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 gap-8 mb-8">
            {VISION_POINTS.map((point, index) => (
              <div 
                key={index}
                className={`flex items-start gap-4 animate-fade-in`}
                style={{ animationDelay: `${index * 150}ms` }}
              >
                <div className="flex-shrink-0 mt-1">
                  <CheckCircle 
                    size={24} 
                    className="text-success" 
                  />
                </div>
                <p className="text-body text-[var(--text-primary)] leading-relaxed">
                  {point}
                </p>
              </div>
            ))}
          </div>
          
          <div className="text-center">
            <Button 
              href="/vision"
              variant="secondary"
              className="inline-flex items-center gap-2 px-6 py-3 border-[var(--accent)] text-[var(--accent)] hover:bg-[var(--accent)]/10"
            >
              Explore Our Full Vision
              <ArrowRight className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
}