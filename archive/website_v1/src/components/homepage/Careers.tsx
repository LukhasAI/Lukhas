'use client';

import { Button } from '@/components/ui/Button';
import { ArrowRight, Users, Code, Palette, Brain } from 'lucide-react';

const openRoles = [
  {
    icon: Brain,
    title: 'AI Research Engineer',
    description: 'Shape the future of human-AI interaction'
  },
  {
    icon: Code,
    title: 'Full-Stack Developer',
    description: 'Build the next generation unified workspace'
  },
  {
    icon: Palette,
    title: 'Product Designer',
    description: 'Design intuitive experiences for complex systems'
  },
  {
    icon: Users,
    title: 'Developer Relations',
    description: 'Help developers build amazing things with Lucas'
  }
];

export default function Careers() {
  return (
    <section className="section-padding bg-[var(--surface)]/20">
      <div className="container">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-h2 font-semibold text-[var(--text-primary)] mb-6">
            Careers
          </h2>
          
          <p className="text-h4 text-[var(--text-primary)] font-normal mb-4">
            Join us in building the unified AI workspace
          </p>
          
          <p className="text-body text-[var(--text-secondary)] mb-12 max-w-2xl mx-auto">
            We're looking for passionate individuals who want to shape the future of 
            human-computer interaction and build tools that amplify human potential.
          </p>
          
          <div className="grid md:grid-cols-2 gap-6 mb-12">
            {openRoles.map((role, index) => {
              const Icon = role.icon;
              return (
                <div
                  key={role.title}
                  className={`p-6 rounded-md bg-[var(--surface)] border border-[var(--border)] hover:border-accent/50 transition-all duration-200 animate-fade-in group`}
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  <div className="flex items-start gap-4">
                    <div className="p-2 rounded-lg bg-accent/10 text-accent group-hover:bg-accent group-hover:text-white transition-all duration-200">
                      <Icon size={20} />
                    </div>
                    <div className="text-left">
                      <h3 className="text-h4 font-medium text-[var(--text-primary)] mb-2">
                        {role.title}
                      </h3>
                      <p className="text-body text-[var(--text-secondary)]">
                        {role.description}
                      </p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button 
              href="/careers"
              size="lg"
              className="group"
            >
              View All Openings
              <ArrowRight size={16} className="ml-2 group-hover:translate-x-1 transition-transform duration-200" />
            </Button>
            
            <Button 
              href="mailto:careers@lucas.ai"
              variant="secondary"
              size="lg"
            >
              Get In Touch
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
}