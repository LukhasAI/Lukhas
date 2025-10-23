/**
 * LUKHAS AI - Email Help Component
 * 
 * Collapsible help system with step-by-step troubleshooting guidance
 * for email delivery issues, following the three-layer tone system.
 */

'use client';

import React, { useState, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { Badge } from '@/components/ui/badge';
import { 
  ChevronDown, 
  ChevronUp, 
  Mail, 
  Search, 
  Shield, 
  Clock, 
  HelpCircle,
  ExternalLink,
  Building,
  RefreshCw,
  AlertCircle
} from 'lucide-react';
import { cn } from '@/lib/utils';

// Import email help i18n
import emailHelpI18n from '@/locales/auth.help.email.json';

interface EmailHelpProps {
  /** Language for i18n */
  locale?: 'en' | 'es';
  /** Sender domain for display */
  senderDomain?: string;
  /** Sender email for display */
  senderEmail?: string;
  /** TTL in minutes */
  ttlMinutes?: number;
  /** Support URL */
  supportUrl?: string;
  /** Show alternative options */
  showAlternatives?: boolean;
  /** Show technical details */
  showTechnical?: boolean;
  /** Show poetic tone sections */
  showPoetic?: boolean;
  /** Variant for different UI contexts */
  variant?: 'default' | 'compact' | 'embedded';
  /** Additional CSS classes */
  className?: string;
  /** Callback when magic link is requested */
  onMagicLinkRequest?: () => void;
  /** Callback when email change is requested */
  onEmailChangeRequest?: () => void;
  /** Callback when support is requested */
  onSupportRequest?: () => void;
}

interface TroubleshootingStep {
  key: string;
  icon: React.ReactNode;
  title: string;
  description: string;
  detail?: string;
  alternatives?: string;
  action?: () => void;
}

export function EmailHelp({
  locale = 'en',
  senderDomain = 'lukhas.ai',
  senderEmail = 'verify@lukhas.ai',
  ttlMinutes = 15,
  supportUrl = '/support',
  showAlternatives = true,
  showTechnical = true,
  showPoetic = false,
  variant = 'default',
  className,
  onMagicLinkRequest,
  onEmailChangeRequest,
  onSupportRequest
}: EmailHelpProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [expandedSteps, setExpandedSteps] = useState<Set<string>>(new Set());
  
  // Get localized strings
  const t = emailHelpI18n[locale];
  
  // Toggle step expansion
  const toggleStep = useCallback((stepKey: string) => {
    setExpandedSteps(prev => {
      const newSet = new Set(prev);
      if (newSet.has(stepKey)) {
        newSet.delete(stepKey);
      } else {
        newSet.add(stepKey);
      }
      return newSet;
    });
  }, []);

  // Generate troubleshooting steps
  const getTroubleshootingSteps = (): TroubleshootingStep[] => [
    {
      key: 'wait',
      icon: <Clock className="w-5 h-5 text-blue-600" />,
      title: t.emailHelp.steps.wait.title,
      description: t.emailHelp.steps.wait.description,
      detail: t.emailHelp.steps.wait.detail
    },
    {
      key: 'checkSpam',
      icon: <Shield className="w-5 h-5 text-orange-600" />,
      title: t.emailHelp.steps.checkSpam.title,
      description: t.emailHelp.steps.checkSpam.description.replace('{senderDomain}', senderDomain),
      detail: t.emailHelp.steps.checkSpam.detail
    },
    {
      key: 'searchInbox',
      icon: <Search className="w-5 h-5 text-green-600" />,
      title: t.emailHelp.steps.searchInbox.title,
      description: t.emailHelp.steps.searchInbox.description
        .replace('{searchTerm}', 'LUKHAS')
        .replace('{senderDomain}', senderDomain),
      detail: t.emailHelp.steps.searchInbox.detail
    },
    {
      key: 'checkFilters',
      icon: <Mail className="w-5 h-5 text-purple-600" />,
      title: t.emailHelp.steps.checkFilters.title,
      description: t.emailHelp.steps.checkFilters.description,
      detail: t.emailHelp.steps.checkFilters.detail
    },
    {
      key: 'corporateBlocking',
      icon: <Building className="w-5 h-5 text-red-600" />,
      title: t.emailHelp.steps.corporateBlocking.title,
      description: t.emailHelp.steps.corporateBlocking.description,
      detail: t.emailHelp.steps.corporateBlocking.detail,
      alternatives: t.emailHelp.steps.corporateBlocking.alternatives
    },
    {
      key: 'tryAgain',
      icon: <RefreshCw className="w-5 h-5 text-indigo-600" />,
      title: t.emailHelp.steps.tryAgain.title,
      description: t.emailHelp.steps.tryAgain.description.replace('{ttlMinutes}', ttlMinutes.toString()),
      detail: t.emailHelp.steps.tryAgain.detail
    }
  ];

  // Render step content
  const renderStep = (step: TroubleshootingStep, index: number) => {
    const isExpanded = expandedSteps.has(step.key);
    
    return (
      <div key={step.key} className="border rounded-lg" data-tone="plain">
        <button
          className="w-full p-4 text-left hover:bg-muted/50 flex items-center gap-3 transition-colors"
          onClick={() => toggleStep(step.key)}
          aria-expanded={isExpanded}
          aria-controls={`step-${step.key}-content`}
          data-tone="plain"
        >
          <div className="flex-shrink-0">
            {step.icon}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <Badge variant="secondary" className="text-xs" data-tone="technical">
                {index + 1}
              </Badge>
              <h4 className="font-medium text-sm" data-tone="plain">
                {step.title}
              </h4>
            </div>
            <p className="text-sm text-muted-foreground" data-tone="plain">
              {step.description}
            </p>
          </div>
          <div className="flex-shrink-0">
            {isExpanded ? (
              <ChevronUp className="w-4 h-4 text-muted-foreground" />
            ) : (
              <ChevronDown className="w-4 h-4 text-muted-foreground" />
            )}
          </div>
        </button>
        
        {isExpanded && (
          <div
            id={`step-${step.key}-content`}
            className="px-4 pb-4 space-y-2"
            data-tone="plain"
          >
            {step.detail && (
              <p className="text-sm text-muted-foreground pl-8" data-tone="technical">
                {step.detail}
              </p>
            )}
            {step.alternatives && (
              <div className="pl-8" data-tone="plain">
                <p className="text-sm font-medium text-blue-700 dark:text-blue-300">
                  {step.alternatives}
                </p>
              </div>
            )}
            {showPoetic && t.emailHelp.poetic[step.key as keyof typeof t.emailHelp.poetic] && (
              <blockquote className="pl-8 text-sm italic text-muted-foreground border-l-2 border-muted ml-6" data-tone="poetic">
                {t.emailHelp.poetic[step.key as keyof typeof t.emailHelp.poetic]}
              </blockquote>
            )}
          </div>
        )}
      </div>
    );
  };

  // Compact variant
  if (variant === 'compact') {
    return (
      <Collapsible open={isOpen} onOpenChange={setIsOpen} className={className}>
        <CollapsibleTrigger asChild>
          <Button 
            variant="ghost" 
            size="sm" 
            className="gap-2 text-sm"
            aria-label={isOpen ? t.emailHelp.toggle.hide : t.emailHelp.toggle.show}
            data-tone="plain"
          >
            <HelpCircle className="w-4 h-4" />
            {t.emailHelp.title}
            {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </Button>
        </CollapsibleTrigger>
        <CollapsibleContent className="mt-2">
          <Card className="border-muted" data-tone="plain">
            <CardContent className="p-4 space-y-2">
              {getTroubleshootingSteps().slice(0, 3).map((step, index) => (
                <div key={step.key} className="flex items-start gap-2 text-sm">
                  <div className="flex-shrink-0 mt-0.5">
                    {step.icon}
                  </div>
                  <div>
                    <span className="font-medium" data-tone="plain">{step.title}:</span>
                    <span className="text-muted-foreground ml-1" data-tone="plain">
                      {step.description}
                    </span>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </CollapsibleContent>
      </Collapsible>
    );
  }

  // Default variant
  return (
    <div className={cn('space-y-4', className)} data-tone="plain">
      <Collapsible open={isOpen} onOpenChange={setIsOpen}>
        <CollapsibleTrigger asChild>
          <Button 
            variant="outline" 
            className="w-full justify-between gap-2"
            aria-expanded={isOpen}
            aria-controls="email-help-content"
            aria-label={isOpen ? t.accessibility.collapseButton : t.accessibility.expandButton}
            data-tone="plain"
          >
            <div className="flex items-center gap-2">
              <HelpCircle className="w-4 h-4" />
              <span>{t.emailHelp.title}</span>
            </div>
            {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </Button>
        </CollapsibleTrigger>
        
        <CollapsibleContent id="email-help-content">
          <Card data-tone="plain">
            <CardHeader className="pb-4">
              <CardTitle className="text-lg flex items-center gap-2" data-tone="plain">
                <Mail className="w-5 h-5" />
                {t.emailHelp.subtitle}
              </CardTitle>
              {showPoetic && (
                <p className="text-sm text-muted-foreground italic" data-tone="poetic">
                  {t.emailHelp.poetic.waiting}
                </p>
              )}
            </CardHeader>
            
            <CardContent className="space-y-6">
              {/* Troubleshooting Steps */}
              <div className="space-y-3" data-tone="plain">
                <h3 
                  className="font-medium text-base mb-3"
                  id="troubleshooting-steps"
                  data-tone="plain"
                >
                  {t.troubleshooting.title}
                </h3>
                
                <div 
                  className="space-y-2"
                  role="list"
                  aria-labelledby="troubleshooting-steps"
                  aria-label={t.accessibility.stepsList}
                >
                  {getTroubleshootingSteps().map(renderStep)}
                </div>
              </div>

              {/* Alternative Options */}
              {showAlternatives && (
                <div className="border-t pt-4" data-tone="plain">
                  <h3 
                    className="font-medium text-base mb-3"
                    id="alternative-options"
                    data-tone="plain"
                  >
                    {t.emailHelp.alternatives.title}
                  </h3>
                  <p className="text-sm text-muted-foreground mb-4" data-tone="plain">
                    {t.emailHelp.alternatives.description}
                  </p>
                  
                  <div 
                    className="grid gap-3 md:grid-cols-3"
                    role="list"
                    aria-labelledby="alternative-options"
                    aria-label={t.accessibility.alternativesList}
                  >
                    {onMagicLinkRequest && (
                      <Card 
                        className="border-muted hover:border-primary transition-colors cursor-pointer" 
                        onClick={onMagicLinkRequest}
                        role="listitem"
                        data-tone="plain"
                      >
                        <CardContent className="p-3">
                          <div className="text-sm font-medium mb-1" data-tone="plain">
                            {t.emailHelp.alternatives.options.magicLink.title}
                          </div>
                          <div className="text-xs text-muted-foreground mb-2" data-tone="plain">
                            {t.emailHelp.alternatives.options.magicLink.description}
                          </div>
                          <Button size="sm" variant="secondary" className="w-full" data-tone="plain">
                            {t.emailHelp.alternatives.options.magicLink.action}
                          </Button>
                        </CardContent>
                      </Card>
                    )}
                    
                    {onEmailChangeRequest && (
                      <Card 
                        className="border-muted hover:border-primary transition-colors cursor-pointer"
                        onClick={onEmailChangeRequest}
                        role="listitem"
                        data-tone="plain"
                      >
                        <CardContent className="p-3">
                          <div className="text-sm font-medium mb-1" data-tone="plain">
                            {t.emailHelp.alternatives.options.differentEmail.title}
                          </div>
                          <div className="text-xs text-muted-foreground mb-2" data-tone="plain">
                            {t.emailHelp.alternatives.options.differentEmail.description}
                          </div>
                          <Button size="sm" variant="secondary" className="w-full" data-tone="plain">
                            {t.emailHelp.alternatives.options.differentEmail.action}
                          </Button>
                        </CardContent>
                      </Card>
                    )}
                    
                    <Card 
                      className="border-muted hover:border-primary transition-colors cursor-pointer"
                      onClick={onSupportRequest}
                      role="listitem"
                      data-tone="plain"
                    >
                      <CardContent className="p-3">
                        <div className="text-sm font-medium mb-1" data-tone="plain">
                          {t.emailHelp.alternatives.options.support.title}
                        </div>
                        <div className="text-xs text-muted-foreground mb-2" data-tone="plain">
                          {t.emailHelp.alternatives.options.support.description}
                        </div>
                        <Button size="sm" variant="secondary" className="w-full gap-1" data-tone="plain">
                          {t.emailHelp.alternatives.options.support.action}
                          <ExternalLink className="w-3 h-3" />
                        </Button>
                      </CardContent>
                    </Card>
                  </div>
                  
                  {showPoetic && (
                    <blockquote className="mt-4 text-sm italic text-muted-foreground border-l-2 border-muted pl-4" data-tone="poetic">
                      {t.emailHelp.poetic.alternatives}
                    </blockquote>
                  )}
                </div>
              )}

              {/* Technical Details */}
              {showTechnical && (
                <div className="border-t pt-4" data-tone="technical">
                  <h3 className="font-medium text-base mb-3" data-tone="technical">
                    {t.emailHelp.technical.title}
                  </h3>
                  <div className="space-y-2 text-sm font-mono">
                    <div data-tone="technical">
                      {t.emailHelp.technical.sender.replace('{senderEmail}', senderEmail)}
                    </div>
                    <div data-tone="technical">
                      {t.emailHelp.technical.domain.replace('{senderDomain}', senderDomain)}
                    </div>
                    <div data-tone="technical">
                      {t.emailHelp.technical.ttl.replace('{ttlMinutes}', ttlMinutes.toString())}
                    </div>
                    <div data-tone="technical">
                      {t.emailHelp.technical.rateLimit.replace('{limit}', '5')}
                    </div>
                    <div className="text-xs text-muted-foreground" data-tone="technical">
                      {t.emailHelp.technical.ipWhitelist.replace('{ipRanges}', '203.0.113.0/24')}
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </CollapsibleContent>
      </Collapsible>
    </div>
  );
}

export default EmailHelp;