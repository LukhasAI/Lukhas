// LUKHΛS AI Web Studio - Core JavaScript
// Following T4 approach: evidence-first, performance-aware

class LukhasyStudio {
    constructor() {
        this.state = 'BOOT';
        this.guards = {
            isEURegion: this.detectEURegion(),
            isAuthenticated: false,
            reducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches
        };
        this.eventBus = new EventTarget();
        this.init();
    }

    init() {
        console.log('LUKHΛS Studio initializing...');
        this.setupStateMachine();
        this.setupEventListeners();
        this.setupPerformanceObserver();
        this.transitionTo('BG_READY');
    }

    // State Machine Implementation
    setupStateMachine() {
        this.states = {
            BOOT: {
                on: { BG_READY: 'QUOTE_IN' }
            },
            QUOTE_IN: {
                on: { CONSENT_NEEDED: 'CONSENT_PENDING' }
            },
            CONSENT_PENDING: {
                on: {
                    CONSENT_ACCEPTED: 'MARKETING_MODE',
                    CONSENT_REJECTED: 'MARKETING_MODE',
                    CONSENT_PARTIAL: 'MARKETING_MODE'
                }
            },
            MARKETING_MODE: {
                on: {
                    CLICK_LOGIN: 'LOGIN_FLOW',
                    ENTER_STUDIO_IF_AUTH: { target: 'ROUTE_DECISION', guard: 'isAuthenticated' }
                }
            },
            LOGIN_FLOW: {
                on: {
                    TOS_ACCEPTED: 'ROUTE_DECISION',
                    TOS_DECLINED: 'MARKETING_MODE'
                }
            },
            ROUTE_DECISION: {
                on: {
                    FIRST_TIME: 'STUDIO_DEFAULT_PRESET',
                    RETURNING: 'STUDIO_USER_PRESET'
                }
            }
        };
    }

    transitionTo(event, context = {}) {
        const currentState = this.states[this.state];
        if (!currentState || !currentState.on || !currentState.on[event]) {
            console.warn(`No transition for event ${event} from state ${this.state}`);
            return;
        }

        const transition = currentState.on[event];
        let nextState;

        if (typeof transition === 'string') {
            nextState = transition;
        } else if (transition.target && this.checkGuard(transition.guard)) {
            nextState = transition.target;
        }

        if (nextState) {
            console.log(`State transition: ${this.state} → ${nextState} (${event})`);
            this.state = nextState;
            this.onStateEnter(nextState, context);
            
            // Emit for observability
            this.emit('STATE_TRANSITION', { from: this.state, to: nextState, event });
        }
    }

    checkGuard(guardName) {
        if (!guardName) return true;
        return this.guards[guardName] || false;
    }

    onStateEnter(state, context) {
        switch (state) {
            case 'QUOTE_IN':
                this.initQuoteSystem();
                break;
            case 'CONSENT_PENDING':
                this.handleConsentFlow();
                break;
            case 'MARKETING_MODE':
                this.initMarketingMode();
                break;
            case 'STUDIO_DEFAULT_PRESET':
                this.loadStudioPreset('default');
                break;
        }
    }

    // Core Systems
    initQuoteSystem() {
        const quotes = [
            { id: "q1", text: "We build tools that serve human agency.", signedBy: "G. Dominguez", tags: ["ethos","welcome"] },
            { id: "q2", text: "Intelligence that remembers consent before convenience.", signedBy: "G. Dominguez", tags: ["safety"] },
            { id: "q3", text: "The substrate for thought emerges from intentional design.", signedBy: "G. Dominguez", tags: ["philosophy"] },
            { id: "q4", text: "Privacy is not a feature—it's a foundation.", signedBy: "G. Dominguez", tags: ["privacy"] }
        ];

        this.startQuoteRotation(quotes);
        this.transitionTo('CONSENT_NEEDED');
    }

    startQuoteRotation(quotes) {
        let currentIndex = 0;
        
        const rotateQuote = () => {
            const quote = quotes[currentIndex];
            this.displayQuote(quote);
            currentIndex = (currentIndex + 1) % quotes.length;
        };

        // Initial quote
        rotateQuote();
        
        // Set interval for rotation
        setInterval(rotateQuote, 7000);
    }

    displayQuote(quote) {
        const quoteText = document.getElementById('quote-text');
        const quoteAuthor = document.getElementById('quote-author');
        
        if (!quoteText || !quoteAuthor) return;

        // Character-by-character animation if motion enabled
        if (!this.guards.reducedMotion) {
            this.animateQuoteCharacters(quoteText, `"${quote.text}"`);
        } else {
            quoteText.textContent = `"${quote.text}"`;
        }
        
        quoteAuthor.textContent = `— ${quote.signedBy}`;
        
        // Emit for observability
        this.emit('QUOTE_SHOWN', { id: quote.id, text: quote.text });
    }

    animateQuoteCharacters(element, text) {
        element.innerHTML = '';
        element.classList.add('character-animate');
        
        [...text].forEach((char, index) => {
            const span = document.createElement('span');
            span.textContent = char === ' ' ? '\u00A0' : char; // Non-breaking space
            span.style.animationDelay = `${index * 20}ms`;
            element.appendChild(span);
        });
    }

    handleConsentFlow() {
        // Check if consent already given
        const consent = this.getStoredConsent();
        if (consent && consent.version === '1.0.0') {
            this.transitionTo('CONSENT_ACCEPTED');
        } else if (this.guards.isEURegion) {
            // EU users need explicit consent
            this.showConsentBanner();
        } else {
            // Non-EU: functional defaults
            this.transitionTo('CONSENT_ACCEPTED');
        }
    }

    getStoredConsent() {
        try {
            const stored = localStorage.getItem('lukhas_consent_v1');
            return stored ? JSON.parse(stored) : null;
        } catch {
            return null;
        }
    }

    showConsentBanner() {
        // Trigger the Nordic cookies component
        window.dispatchEvent(new CustomEvent('lukhas:show-consent-banner'));
    }

    initMarketingMode() {
        console.log('Marketing mode active');
        this.setupCTAHandlers();
    }

    setupCTAHandlers() {
        const enterBtn = document.querySelector('.btn-primary');
        if (enterBtn) {
            enterBtn.addEventListener('click', (e) => {
                e.preventDefault();
                if (this.guards.isAuthenticated) {
                    this.transitionTo('ENTER_STUDIO_IF_AUTH');
                } else {
                    this.transitionTo('CLICK_LOGIN');
                }
            });
        }
    }

    loadStudioPreset(presetName) {
        console.log(`Loading studio preset: ${presetName}`);
        // Future: Load actual studio interface
        this.emit('STUDIO_LOADED', { preset: presetName });
    }

    // Utilities
    detectEURegion() {
        // Simple detection - in production, use IP geolocation
        const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        const euTimezones = [
            'Europe/London', 'Europe/Berlin', 'Europe/Paris', 'Europe/Rome',
            'Europe/Madrid', 'Europe/Amsterdam', 'Europe/Brussels', 'Europe/Vienna'
        ];
        return euTimezones.some(tz => timezone.includes(tz.split('/')[1]));
    }

    setupEventListeners() {
        // Cookie preferences
        window.addEventListener('lukhas:consent-accepted', (e) => {
            this.transitionTo('CONSENT_ACCEPTED', e.detail);
        });

        window.addEventListener('lukhas:consent-rejected', (e) => {
            this.transitionTo('CONSENT_REJECTED', e.detail);
        });

        window.addEventListener('lukhas:open-cookie-prefs', () => {
            // Handled by Nordic cookies component
        });

        // Navigation
        document.addEventListener('click', (e) => {
            if (e.target.matches('.nav-link')) {
                this.handleNavigation(e);
            }
        });
    }

    handleNavigation(e) {
        e.preventDefault();
        const href = e.target.getAttribute('href');
        
        if (href === '/legal/terms-eu.html') {
            window.location.href = href;
            return;
        }

        // SPA-style navigation for other links
        const target = href.replace('#', '');
        console.log(`Navigating to: ${target}`);
    }

    setupPerformanceObserver() {
        // Monitor Core Web Vitals
        if ('PerformanceObserver' in window) {
            const observer = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    if (entry.entryType === 'largest-contentful-paint') {
                        this.emit('LCP_MEASURED', { value: entry.startTime });
                    }
                }
            });
            
            observer.observe({ entryTypes: ['largest-contentful-paint'] });
        }
    }

    // Event System
    emit(eventName, detail = {}) {
        this.eventBus.dispatchEvent(new CustomEvent(eventName, { detail }));
        
        // Log for observability (matching visual_studio.json spec)
        const observabilityEvents = [
            'QUOTE_SHOWN', 'CONSENT_DECISION', 'LOGIN_SUCCESS', 'STUDIO_LOADED',
            'STATE_TRANSITION', 'LCP_MEASURED'
        ];
        
        if (observabilityEvents.includes(eventName)) {
            console.log(`📊 ${eventName}:`, detail);
        }
    }

    on(eventName, handler) {
        this.eventBus.addEventListener(eventName, handler);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.lukhasyStudio = new LukhasyStudio();
});

// Performance Budget Monitoring (T4 requirement)
window.addEventListener('load', () => {
    setTimeout(() => {
        const navigation = performance.getEntriesByType('navigation')[0];
        const lcp = performance.getEntriesByType('largest-contentful-paint')[0];
        
        const metrics = {
            LCP: lcp ? lcp.startTime : 0,
            FCP: navigation ? navigation.loadEventEnd - navigation.loadEventStart : 0
        };

        // Budget checks from visual_studio.json
        const budgets = { LCP_ms: 2500, CLS: 0.1, TBT_ms: 200 };
        
        if (metrics.LCP > budgets.LCP_ms) {
            console.warn(`🚨 LCP budget exceeded: ${metrics.LCP}ms > ${budgets.LCP_ms}ms`);
        }

        console.log('📈 Performance Metrics:', metrics);
    }, 0);
});
