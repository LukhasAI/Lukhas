/**
 * LUKHAS AI - Code Help Modal Component
 *
 * Comprehensive micro-modal combining ResendControl + EmailHelp
 * with accessibility features, three-layer tone compliance, and mobile support.
 */

'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import {
  HelpCircle,
  Mail,
  X,
  ExternalLink,
  RefreshCw,
  AlertCircle,
  Clock,
  Shield,
  Phone,
  MessageSquare
} from 'lucide-react';
import { cn } from '@/lib/utils';

// Import existing components
import { ResendControl } from './ResendControl';
import { EmailHelp } from './EmailHelp';

// Import localization
import codeHelpI18n from '@/locales/code-help-modal.json';

// Import support email utility
import { buildSupportMailto, collectBrowserInfo } from '../lib/mailto';

interface CodeHelpModalProps {
  /** Whether the modal is open */
  open: boolean;
  /** Callback when modal close is requested */
  onOpenChange: (open: boolean) => void;
  /** Email address for verification */
  email: string;
  /** Purpose of verification */
  purpose?: 'login' | 'register' | 'password-reset' | 'email-verification' | 'phone-verification';
  /** User's authentication tier */
  userTier?: 'T1' | 'T2' | 'T3' | 'T4' | 'T5';
  /** Language for localization */
  locale?: 'en' | 'es';
  /** Sender domain for email help */
  senderDomain?: string;
  /** Support URL for help links */
  supportUrl?: string;
  /** REALM/ZONE for enterprise support */
  realm?: string;
  zone?: string;
  /** User alias for support context */
  userAlias?: string;
  /** Show alternative authentication flows */
  showAlternatives?: boolean;
  /** Show technical details */
  showTechnical?: boolean;
  /** Additional CSS classes */
  className?: string;
  /** Callback for alternative auth method selection */
  onAlternativeSelected?: (method: 'magic-link' | 'passkey' | 'support') => void;
  /** Callback for code resend success */
  onCodeSent?: (result: { requestId: string; success: boolean }) => void;
  /** Callback for rate limit exceeded */
  onRateLimited?: (resetTime: number) => void;
}

export function CodeHelpModal({
  open,
  onOpenChange,
  email,
  purpose = 'login',
  userTier,
  locale = 'en',
  senderDomain = 'lukhas.ai',
  supportUrl = '/support',
  realm,
  zone,
  userAlias,
  showAlternatives = true,
  showTechnical = true,
  className,
  onAlternativeSelected,
  onCodeSent,
  onRateLimited
}: CodeHelpModalProps) {
  const [activeTab, setActiveTab] = useState<'resend' | 'troubleshoot' | 'support'>('resend');
  const [browserInfo, setBrowserInfo] = useState<Record<string, any>>({});

  // Focus management refs
  const closeButtonRef = useRef<HTMLButtonElement>(null);
  const previousFocusRef = useRef<Element | null>(null);

  // Get localized strings
  const t = codeHelpI18n[locale] || codeHelpI18n.en;

  // Collect browser information on mount
  useEffect(() => {
    setBrowserInfo(collectBrowserInfo());
  }, []);

  // Focus management - focus close button when modal opens
  useEffect(() => {
    if (open) {
      // Store previous focus
      previousFocusRef.current = document.activeElement;
      // Focus close button after a short delay for transition
      const timer = setTimeout(() => {
        closeButtonRef.current?.focus();
      }, 100);
      return () => clearTimeout(timer);
    } else {
      // Restore previous focus when modal closes
      if (previousFocusRef.current instanceof HTMLElement) {
        previousFocusRef.current.focus();
      }
    }
  }, [open]);

  // Handle modal close
  const handleClose = useCallback((newOpen: boolean) => {
    onOpenChange(newOpen);
  }, [onOpenChange]);

  // Handle support email generation
  const handleSupportEmail = useCallback(() => {
    const subject = t.support.email.subject.replace('{purpose}', purpose).replace('{email}', email);
    const context = {
      email,
      purpose,
      userTier,
      realm,
      zone,
      userAlias,
      senderDomain,
      timestamp: new Date().toISOString()
    };

    const mailtoUrl = buildSupportMailto({
      subject,
      body: t.support.email.body[purpose] || t.support.email.body.default,
      context,
      browserInfo,
      locale
    });

    // Open mailto link
    window.location.href = mailtoUrl;

    // Track support request
    onAlternativeSelected?.('support');
  }, [
    t.support.email.subject,
    t.support.email.body,
    purpose,
    email,
    userTier,
    realm,
    zone,
    userAlias,
    senderDomain,
    browserInfo,
    locale,
    onAlternativeSelected
  ]);

  // Handle alternative auth methods
  const handleAlternativeMethod = useCallback((method: 'magic-link' | 'passkey' | 'support') => {
    if (method === 'support') {
      handleSupportEmail();
    } else {
      onAlternativeSelected?.(method);
    }
    handleClose(false);
  }, [handleSupportEmail, onAlternativeSelected, handleClose]);

  // Handle keyboard navigation
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    if (event.key === 'Escape') {
      handleClose(false);
    }
  }, [handleClose]);

  useEffect(() => {
    if (open) {
      document.addEventListener('keydown', handleKeyDown);
      return () => document.removeEventListener('keydown', handleKeyDown);
    }
  }, [open, handleKeyDown]);

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent
        className={cn(
          'max-w-2xl max-h-[90vh] overflow-y-auto',
          'sm:max-w-lg md:max-w-xl lg:max-w-2xl',
          className
        )}
        aria-labelledby="code-help-modal-title"
        aria-describedby="code-help-modal-description"
        data-tone="plain"
      >
        {/* Close Button with Focus Management */}
        <Button
          ref={closeButtonRef}
          variant="ghost"
          size="sm"
          className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
          onClick={() => handleClose(false)}
          aria-label={t.accessibility.closeModal}
          data-tone="plain"
        >
          <X className="h-4 w-4" />
        </Button>

        <DialogHeader className="pb-4" data-tone="plain">
          <DialogTitle
            id="code-help-modal-title"
            className="text-xl font-semibold flex items-center gap-2"
            data-tone="plain"
          >
            <HelpCircle className="w-5 h-5" />
            {t.modal.title}
          </DialogTitle>
          <DialogDescription
            id="code-help-modal-description"
            className="text-sm text-muted-foreground"
            data-tone="plain"
          >
            {t.modal.description.replace('{email}', email)}
          </DialogDescription>

          {/* Context Badge */}
          <div className="flex items-center gap-2 mt-2">
            <Badge variant="secondary" className="text-xs" data-tone="technical">
              {purpose}
            </Badge>
            {userTier && (
              <Badge variant="outline" className="text-xs" data-tone="technical">
                {userTier}
              </Badge>
            )}
            {realm && (
              <Badge variant="outline" className="text-xs" data-tone="technical">
                {realm}{zone ? `.${zone}` : ''}
              </Badge>
            )}
          </div>
        </DialogHeader>

        {/* Main Content with Tabs */}
        <Tabs
          value={activeTab}
          onValueChange={(value) => setActiveTab(value as any)}
          className="w-full"
          data-tone="plain"
        >
          <TabsList className="grid w-full grid-cols-3" data-tone="plain">
            <TabsTrigger value="resend" className="gap-1" data-tone="plain">
              <RefreshCw className="w-4 h-4" />
              <span className="hidden sm:inline">{t.tabs.resend.title}</span>
              <span className="sm:hidden">{t.tabs.resend.short}</span>
            </TabsTrigger>
            <TabsTrigger value="troubleshoot" className="gap-1" data-tone="plain">
              <Mail className="w-4 h-4" />
              <span className="hidden sm:inline">{t.tabs.troubleshoot.title}</span>
              <span className="sm:hidden">{t.tabs.troubleshoot.short}</span>
            </TabsTrigger>
            <TabsTrigger value="support" className="gap-1" data-tone="plain">
              <MessageSquare className="w-4 h-4" />
              <span className="hidden sm:inline">{t.tabs.support.title}</span>
              <span className="sm:hidden">{t.tabs.support.short}</span>
            </TabsTrigger>
          </TabsList>

          {/* Resend Tab */}
          <TabsContent value="resend" className="mt-4 space-y-4" data-tone="plain">
            <Card data-tone="plain">
              <CardHeader className="pb-3">
                <CardTitle className="text-base flex items-center gap-2" data-tone="plain">
                  <RefreshCw className="w-4 h-4" />
                  {t.tabs.resend.subtitle}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ResendControl
                  email={email}
                  purpose={purpose}
                  locale={locale}
                  userTier={userTier}
                  onCodeSent={onCodeSent}
                  onRateLimited={onRateLimited}
                  variant="default"
                  showHelp={false}
                  className="mb-4"
                />
                <div className="text-xs text-muted-foreground" data-tone="technical">
                  {t.tabs.resend.note.replace('{senderDomain}', senderDomain)}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Troubleshooting Tab */}
          <TabsContent value="troubleshoot" className="mt-4" data-tone="plain">
            <EmailHelp
              locale={locale}
              senderDomain={senderDomain}
              supportUrl={supportUrl}
              showAlternatives={false}
              showTechnical={showTechnical}
              showPoetic={false}
              variant="embedded"
              onMagicLinkRequest={() => handleAlternativeMethod('magic-link')}
              onEmailChangeRequest={() => setActiveTab('support')}
              onSupportRequest={() => setActiveTab('support')}
            />
          </TabsContent>

          {/* Support Tab */}
          <TabsContent value="support" className="mt-4 space-y-4" data-tone="plain">
            <Card data-tone="plain">
              <CardHeader className="pb-3">
                <CardTitle className="text-base flex items-center gap-2" data-tone="plain">
                  <MessageSquare className="w-4 h-4" />
                  {t.tabs.support.subtitle}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="text-sm text-muted-foreground" data-tone="plain">
                  {t.tabs.support.description}
                </div>

                {/* Support Options */}
                <div className="grid gap-3 md:grid-cols-2">
                  {/* Email Support */}
                  <Card
                    className="border-muted hover:border-primary transition-colors cursor-pointer"
                    onClick={handleSupportEmail}
                    data-tone="plain"
                  >
                    <CardContent className="p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <Mail className="w-4 h-4" />
                        <span className="font-medium text-sm" data-tone="plain">
                          {t.support.options.email.title}
                        </span>
                      </div>
                      <p className="text-xs text-muted-foreground mb-3" data-tone="plain">
                        {t.support.options.email.description}
                      </p>
                      <Button size="sm" variant="secondary" className="w-full gap-1" data-tone="plain">
                        {t.support.options.email.action}
                        <ExternalLink className="w-3 h-3" />
                      </Button>
                    </CardContent>
                  </Card>

                  {/* Live Support (if available) */}
                  <Card
                    className="border-muted hover:border-primary transition-colors cursor-pointer"
                    onClick={() => window.open(supportUrl, '_blank')}
                    data-tone="plain"
                  >
                    <CardContent className="p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <Phone className="w-4 h-4" />
                        <span className="font-medium text-sm" data-tone="plain">
                          {t.support.options.live.title}
                        </span>
                      </div>
                      <p className="text-xs text-muted-foreground mb-3" data-tone="plain">
                        {t.support.options.live.description}
                      </p>
                      <Button size="sm" variant="secondary" className="w-full gap-1" data-tone="plain">
                        {t.support.options.live.action}
                        <ExternalLink className="w-3 h-3" />
                      </Button>
                    </CardContent>
                  </Card>
                </div>

                {/* Context Information */}
                {showTechnical && (
                  <div className="border-t pt-4 space-y-2" data-tone="technical">
                    <h4 className="text-sm font-medium" data-tone="technical">
                      {t.support.context.title}
                    </h4>
                    <div className="text-xs font-mono space-y-1">
                      <div>Email: {email}</div>
                      <div>Purpose: {purpose}</div>
                      {userTier && <div>Tier: {userTier}</div>}
                      {realm && <div>Realm: {realm}{zone ? `.${zone}` : ''}</div>}
                      <div>Browser: {browserInfo.browser || 'Unknown'}</div>
                      <div>OS: {browserInfo.os || 'Unknown'}</div>
                      <div>Timestamp: {new Date().toLocaleString(locale)}</div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Alternative Authentication Methods */}
            {showAlternatives && (
              <Card data-tone="plain">
                <CardHeader className="pb-3">
                  <CardTitle className="text-base flex items-center gap-2" data-tone="plain">
                    <Shield className="w-4 h-4" />
                    {t.alternatives.title}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-sm text-muted-foreground mb-4" data-tone="plain">
                    {t.alternatives.description}
                  </div>

                  <div className="grid gap-3 sm:grid-cols-2">
                    {/* Magic Link */}
                    <Button
                      variant="outline"
                      className="h-auto p-3 flex flex-col items-start gap-2"
                      onClick={() => handleAlternativeMethod('magic-link')}
                      data-tone="plain"
                    >
                      <div className="flex items-center gap-2 text-left">
                        <Mail className="w-4 h-4" />
                        <span className="font-medium">{t.alternatives.options.magicLink.title}</span>
                      </div>
                      <span className="text-xs text-muted-foreground text-left">
                        {t.alternatives.options.magicLink.description}
                      </span>
                    </Button>

                    {/* Passkey (if supported) */}
                    {userTier && ['T2', 'T3', 'T4', 'T5'].includes(userTier) && (
                      <Button
                        variant="outline"
                        className="h-auto p-3 flex flex-col items-start gap-2"
                        onClick={() => handleAlternativeMethod('passkey')}
                        data-tone="plain"
                      >
                        <div className="flex items-center gap-2 text-left">
                          <Shield className="w-4 h-4" />
                          <span className="font-medium">{t.alternatives.options.passkey.title}</span>
                        </div>
                        <span className="text-xs text-muted-foreground text-left">
                          {t.alternatives.options.passkey.description}
                        </span>
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>

        {/* Footer with Quick Actions */}
        <div className="flex justify-between items-center pt-4 border-t" data-tone="plain">
          <div className="text-xs text-muted-foreground" data-tone="technical">
            {t.footer.version} • {t.footer.updated}
          </div>
          <div className="flex gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => handleClose(false)}
              data-tone="plain"
            >
              {t.footer.close}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

export default CodeHelpModal;
