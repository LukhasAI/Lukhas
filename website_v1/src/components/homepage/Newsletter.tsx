'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Mail, CheckCircle } from 'lucide-react';

export default function Newsletter() {
  const [email, setEmail] = useState('');
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;
    
    setIsLoading(true);
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    setIsSubscribed(true);
    setIsLoading(false);
    setEmail('');
  };

  return (
    <section className="section-padding bg-gradient-to-r from-accent/5 via-info/5 to-success/5">
      <div className="container">
        <div className="max-w-2xl mx-auto text-center">
          {!isSubscribed ? (
            <>
              <div className="mb-8">
                <div className="inline-flex p-3 rounded-full bg-accent/10 text-accent mb-6">
                  <Mail size={32} />
                </div>
                <h2 className="text-h2 font-semibold text-[var(--text-primary)] mb-4">
                  Stay Updated
                </h2>
                <p className="text-body text-[var(--text-secondary)]">
                  Get early access to new features, product updates, and insights 
                  from the Lucas team. No spam, unsubscribe anytime.
                </p>
              </div>
              
              <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1">
                  <Input
                    type="email"
                    placeholder="Enter your email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="w-full"
                  />
                </div>
                <Button 
                  type="submit" 
                  disabled={isLoading}
                  className="sm:px-8"
                >
                  {isLoading ? 'Subscribing...' : 'Subscribe'}
                </Button>
              </form>
              
              <p className="text-small text-[var(--text-secondary)] mt-4">
                No spam. Unsubscribe anytime.
              </p>
            </>
          ) : (
            <div className="animate-fade-in">
              <div className="inline-flex p-3 rounded-full bg-success/10 text-success mb-6">
                <CheckCircle size={32} />
              </div>
              <h2 className="text-h2 font-semibold text-[var(--text-primary)] mb-4">
                You're all set!
              </h2>
              <p className="text-body text-[var(--text-secondary)]">
                Thanks for subscribing. You'll receive updates about Lucas 
                and be the first to know about new features.
              </p>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}