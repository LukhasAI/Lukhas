'use client';

export default function About() {
  return (
    <section className="section-padding bg-[var(--background)]">
      <div className="container">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <h2 id="about" className="text-h2 font-semibold text-[var(--text-primary)] mb-6">
              About <span className="bg-gradient-to-r from-[var(--gradient-start)] to-[var(--gradient-end)] bg-clip-text text-transparent">LUKHAS</span>
            </h2>
            <p className="text-lg text-[var(--text-secondary)] max-w-3xl mx-auto">
              We are developing AI tools and interfaces designed to enhance productivity and creativity.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div className="space-y-6">
              <p className="text-h4 text-[var(--text-primary)] font-normal leading-relaxed">
                We focus on creating user-friendly AI interfaces and tools that are intuitive, efficient, and designed to work seamlessly with existing workflows.
              </p>
              
              <p className="text-body text-[var(--text-secondary)] leading-relaxed">
                Through careful design and engineering, we're building AI tools that help users accomplish their goals more effectively 
                while maintaining privacy and security standards.
              </p>
              
              <p className="text-body text-[var(--text-secondary)] leading-relaxed">
                Our modular approach allows users to integrate the specific AI capabilities they need, whether for productivity enhancement, 
                creative workflows, or specialized applications.
              </p>
              
              <div className="bg-gradient-to-r from-[var(--accent)]/10 to-[var(--gradient-end)]/10 p-4 rounded-xl border border-[var(--accent)]/20">
                <p className="text-sm text-[var(--text-secondary)] italic">
                  "We believe the best AI tools are those that enhance human capabilities rather than replace them, 
                  working alongside users to amplify their creativity and productivity."
                </p>
              </div>
            </div>
            
            <div className="bg-gradient-to-br from-[var(--surface)] to-[var(--background)] p-8 rounded-2xl border border-[var(--border)]">
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-[var(--accent)] mb-2">Our Mission</h3>
                  <p className="text-[var(--text-secondary)] text-sm leading-relaxed">
                    To develop AI tools that enhance productivity and creativity while respecting user privacy and choice.
                  </p>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold text-[var(--accent)] mb-2">Our Vision</h3>
                  <p className="text-[var(--text-secondary)] text-sm leading-relaxed">
                    A future where AI tools and human intelligence work together effectively to solve complex problems 
                    and enhance creative workflows.
                  </p>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold text-[var(--accent)] mb-2">Our Values</h3>
                  <p className="text-[var(--text-secondary)] text-sm leading-relaxed">
                    Innovation, transparency, user privacy, ethical development practices, and building tools that genuinely help people.
                  </p>
                </div>
              </div>
            </div>
          </div>
          
          {/* Key Focus Areas */}
          <div className="mt-16">
            <div className="text-center mb-12">
              <h3 className="text-2xl font-semibold text-[var(--text-primary)] mb-4">Our Focus Areas</h3>
              <p className="text-[var(--text-secondary)] max-w-3xl mx-auto">
                We're developing AI tools across multiple domains to support different aspects of productivity and creativity.
              </p>
            </div>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="p-6 rounded-xl bg-[var(--surface)]/30 border border-[var(--border)] hover:border-[var(--accent)]/50 transition-colors">
                <div className="w-12 h-12 bg-[var(--accent)]/10 rounded-xl flex items-center justify-center mb-4">
                  <div className="text-[var(--accent)] text-xl">🎨</div>
                </div>
                <h4 className="font-semibold text-[var(--text-primary)] mb-2">Creative Tools</h4>
                <p className="text-sm text-[var(--text-secondary)]">AI-powered interfaces for creative workflows, content generation, and design assistance</p>
              </div>
              
              <div className="p-6 rounded-xl bg-[var(--surface)]/30 border border-[var(--border)] hover:border-[var(--accent)]/50 transition-colors">
                <div className="w-12 h-12 bg-[var(--accent)]/10 rounded-xl flex items-center justify-center mb-4">
                  <div className="text-[var(--accent)] text-xl">⚡</div>
                </div>
                <h4 className="font-semibold text-[var(--text-primary)] mb-2">Productivity</h4>
                <p className="text-sm text-[var(--text-secondary)]">Intelligent automation and workflow enhancement tools for professionals</p>
              </div>
              
              <div className="p-6 rounded-xl bg-[var(--surface)]/30 border border-[var(--border)] hover:border-[var(--accent)]/50 transition-colors">
                <div className="w-12 h-12 bg-[var(--accent)]/10 rounded-xl flex items-center justify-center mb-4">
                  <div className="text-[var(--accent)] text-xl">🔒</div>
                </div>
                <h4 className="font-semibold text-[var(--text-primary)] mb-2">Privacy & Security</h4>
                <p className="text-sm text-[var(--text-secondary)]">User-controlled AI tools with strong privacy protections and ethical safeguards</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}