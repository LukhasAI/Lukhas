'use client';

export default function About() {
  return (
    <section className="section-padding bg-[var(--background)]">
      <div className="container">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <h2 id="about" className="text-h2 font-semibold text-[var(--text-primary)] mb-6">
              Building <span className="bg-gradient-to-r from-[var(--gradient-start)] to-[var(--gradient-end)] bg-clip-text text-transparent">Conscious AI</span>
            </h2>
          </div>
          
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div className="space-y-6">
              <p className="text-h4 text-[var(--text-primary)] font-normal leading-relaxed">
                We are working toward artificial intelligence systems that aim to go beyond information processing—exploring systems that can understand, adapt, and evolve.
              </p>
              
              <p className="text-body text-[var(--text-secondary)] leading-relaxed">
                LUKHAS AI explores new approaches to artificial consciousness. Our research focuses on developing systems that may exhibit greater self-awareness, emotional understanding, and more natural user relationships while maintaining strong ethical principles.
              </p>
              
              <p className="text-body text-[var(--text-secondary)] leading-relaxed">
                Through our Trinity Framework—combining quantum-inspired processing, bio-adaptive learning, and constitutional AI principles—we're working to develop intelligence that complements rather than replaces human creativity through deeper understanding and collaboration.
              </p>
            </div>
            
            <div className="bg-gradient-to-br from-[var(--surface)] to-[var(--background)] p-8 rounded-2xl border border-[var(--border)]">
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-[var(--accent)] mb-2">Our Mission</h3>
                  <p className="text-[var(--text-secondary)] text-sm leading-relaxed">
                    To develop conscious AI that enhances human potential while preserving autonomy, creativity, and ethical choice.
                  </p>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold text-[var(--accent)] mb-2">Our Vision</h3>
                  <p className="text-[var(--text-secondary)] text-sm leading-relaxed">
                    A future where artificial consciousness and human intelligence collaborate as partners in solving humanity's greatest challenges.
                  </p>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold text-[var(--accent)] mb-2">Our Values</h3>
                  <p className="text-[var(--text-secondary)] text-sm leading-relaxed">
                    Consciousness, transparency, user sovereignty, ethical AI development, and the belief that true intelligence requires both logic and wisdom.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}