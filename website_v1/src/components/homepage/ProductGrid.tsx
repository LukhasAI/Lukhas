'use client';

import { Card, CardContent, CardDescription, CardTitle } from '@/components/ui/Card';
import { PRODUCTS } from '@/lib/constants';
import { ExternalLink, Zap, Wallet, Mail, Shield } from 'lucide-react';

const productIcons = {
  'LUKHAS Studio': Zap,
  'LUKHAS Identity': Shield,
  'LUKHAS Wallet': Wallet,
  'LUKHAS Connect': Mail,
  'NIAS Intelligence': ExternalLink,
};

export default function ProductGrid() {
  return (
    <section id="our-products" className="section-padding bg-[var(--background)]">
      <div className="container">
        <div className="text-center mb-16">
          <h2 className="text-h2 font-semibold text-[var(--text-primary)] mb-4">
            The <span className="bg-gradient-to-r from-[var(--gradient-start)] to-[var(--gradient-end)] bg-clip-text text-transparent">LUKHAS Ecosystem</span>
          </h2>
          <p className="text-body text-[var(--text-secondary)] max-w-3xl mx-auto leading-relaxed">
            A developing suite of AI tools that aim to adapt to your needs, learn from your patterns,
            and evolve with your workflow—exploring more personalized intelligence experiences.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
          {PRODUCTS.map((product, index) => {
            const Icon = productIcons[product.name as keyof typeof productIcons] || Zap;
            const isExternal = product.href.startsWith('http');
            
            return (
              <Card
                key={product.name}
                hover={true}
                className={`p-6 group cursor-pointer animate-fade-in`}
                style={{ animationDelay: `${index * 100}ms` }}
                onClick={() => window.open(product.href, isExternal ? '_blank' : '_self')}
              >
                <CardContent className="p-0">
                  <div className="flex items-start gap-4">
                    <div className="p-3 rounded-lg bg-accent/10 text-accent group-hover:bg-accent group-hover:text-white transition-all duration-200">
                      <Icon size={24} />
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2">
                        <CardTitle className="text-h4 group-hover:text-accent transition-colors duration-200">
                          {product.name}
                        </CardTitle>
                        {isExternal && (
                          <ExternalLink size={16} className="text-[var(--text-secondary)] group-hover:text-accent transition-colors duration-200" />
                        )}
                      </div>
                      
                      <CardDescription className="text-[var(--text-secondary)] leading-relaxed">
                        {product.desc}
                      </CardDescription>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </section>
  );
}