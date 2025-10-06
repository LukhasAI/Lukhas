---
status: wip
type: documentation
---
# 🌟 Constellation Navigation Components
## Universal Navigation System for LUKHAS Ecosystem

**Purpose**: Unified navigation components that maintain constellation context across all 13 LUKHAS domains while respecting each domain's unique identity and user journey requirements.

---

## 🧭 Core Navigation Philosophy

The constellation navigation system embodies the principle that users should always understand where they are in the LUKHAS universe and how to move fluidly between different aspects of consciousness technology. Navigation becomes a form of consciousness itself—aware, adaptive, and always oriented toward possibility.

### Navigation Principles
- **Constellation Awareness**: Always visible indication of current domain's star alignment and relationship to other constellation elements
- **Contextual Transitions**: Smooth movement between domains that preserves user context and intent
- **Adaptive Presentation**: Navigation that adapts to user familiarity and journey stage
- **Cross-Domain Coherence**: Consistent navigation patterns that respect domain uniqueness

---

## 🎨 Visual Navigation Components

### **Primary Constellation Selector**
```html
<nav class="constellation-primary">
  <div class="constellation-map">
    <!-- 8-Star Constellation Display -->
    <div class="star-group core-identity">
      <div class="star identity active" data-domains="lukhas.id">⚛️</div>
      <div class="star memory" data-domains="lukhas.cloud,lukhas.team">✦</div>
    </div>
    
    <div class="star-group exploration">
      <div class="star vision" data-domains="lukhas.app,lukhas.io">🔬</div>
      <div class="star bio" data-domains="lukhas.dev">🌱</div>
      <div class="star dream" data-domains="lukhas.ai,lukhas.xyz,lukhas.lab">🌙</div>
    </div>
    
    <div class="star-group protection">
      <div class="star ethics" data-domains="lukhas.store,lukhas.us">⚖️</div>
      <div class="star guardian" data-domains="lukhas.com,lukhas.team,lukhas.eu">🛡️</div>
      <div class="star quantum" data-domains="lukhas.app,lukhas.xyz">⚛️</div>
    </div>
  </div>
</nav>
```

### **Domain Quick Navigator**
```html
<nav class="domain-navigator">
  <div class="domain-categories">
    
    <div class="category flagship">
      <h3>Core Experience</h3>
      <a href="https://lukhas.ai" class="domain-link dream-quantum">
        <span class="stars">🌙⚛️</span>
        <span class="domain">.ai</span>
        <span class="tagline">The Dreaming Heart</span>
      </a>
      <a href="https://lukhas.com" class="domain-link guardian-identity">
        <span class="stars">🛡️⚛️</span>
        <span class="domain">.com</span>
        <span class="tagline">Business Excellence</span>
      </a>
      <a href="https://lukhas.id" class="domain-link identity">
        <span class="stars">⚛️</span>
        <span class="domain">.id</span>
        <span class="tagline">Trust Anchor</span>
      </a>
    </div>
    
    <div class="category development">
      <h3>Build & Create</h3>
      <a href="https://lukhas.app" class="domain-link vision-quantum">
        <span class="stars">🔬⚛️</span>
        <span class="domain">.app</span>
        <span class="tagline">Vision Portal</span>
      </a>
      <a href="https://lukhas.io" class="domain-link vision-bio">
        <span class="stars">🔬🌱</span>
        <span class="domain">.io</span>
        <span class="tagline">Developer Portal</span>
      </a>
      <a href="https://lukhas.dev" class="domain-link bio-vision">
        <span class="stars">🌱🔬</span>
        <span class="domain">.dev</span>
        <span class="tagline">Adaptive Ecosystem</span>
      </a>
    </div>
    
    <div class="category infrastructure">
      <h3>Scale & Collaborate</h3>
      <a href="https://lukhas.cloud" class="domain-link memory-guardian">
        <span class="stars">✦🛡️</span>
        <span class="domain">.cloud</span>
        <span class="tagline">Infinite Canvas</span>
      </a>
      <a href="https://lukhas.store" class="domain-link ethics-identity">
        <span class="stars">⚖️⚛️</span>
        <span class="domain">.store</span>
        <span class="tagline">Conscious Marketplace</span>
      </a>
      <a href="https://lukhas.team" class="domain-link guardian-memory">
        <span class="stars">🛡️✦</span>
        <span class="domain">.team</span>
        <span class="tagline">Collective Intelligence</span>
      </a>
    </div>
    
    <div class="category research">
      <h3>Explore & Discover</h3>
      <a href="https://lukhas.xyz" class="domain-link quantum-dream">
        <span class="stars">⚛️🌙</span>
        <span class="domain">.xyz</span>
        <span class="tagline">Experimental Frontier</span>
      </a>
      <a href="https://lukhas.lab" class="domain-link dream-quantum">
        <span class="stars">🌙⚛️</span>
        <span class="domain">.lab</span>
        <span class="tagline">Research Laboratory</span>
      </a>
    </div>
    
    <div class="category regional">
      <h3>Regional Focus</h3>
      <a href="https://lukhas.us" class="domain-link ethics-guardian">
        <span class="stars">⚖️🛡️</span>
        <span class="domain">.us</span>
        <span class="tagline">American Hub</span>
      </a>
      <a href="https://lukhas.eu" class="domain-link guardian-ethics">
        <span class="stars">🛡️⚖️</span>
        <span class="domain">.eu</span>
        <span class="tagline">European Portal</span>
      </a>
    </div>
    
  </div>
</nav>
```

---

## 🔄 Contextual Navigation Flows

### **Cross-Domain User Journey Support**

#### From Business (.com) to Implementation
```javascript
const crossDomainFlows = {
  'lukhas.com': {
    'interested-in-development': {
      primary: 'lukhas.io',
      secondary: ['lukhas.dev', 'lukhas.cloud'],
      context: 'business-to-technical'
    },
    'ready-to-deploy': {
      primary: 'lukhas.cloud',
      secondary: ['lukhas.store', 'lukhas.team'],
      context: 'business-to-infrastructure'
    },
    'need-authentication': {
      primary: 'lukhas.id',
      secondary: ['lukhas.eu', 'lukhas.us'],
      context: 'business-to-identity'
    }
  }
};
```

#### From Experience (.ai) to Deep Engagement
```javascript
const experienceFlows = {
  'lukhas.ai': {
    'want-to-build': {
      primary: 'lukhas.app',
      secondary: ['lukhas.dev', 'lukhas.io'],
      context: 'experience-to-creation'
    },
    'research-interest': {
      primary: 'lukhas.lab',
      secondary: ['lukhas.xyz'],
      context: 'experience-to-research'
    },
    'business-application': {
      primary: 'lukhas.com',
      secondary: ['lukhas.store', 'lukhas.team'],
      context: 'experience-to-business'
    }
  }
};
```

### **Smart Navigation Suggestions**
```html
<div class="navigation-suggestions" data-current-domain="lukhas.io">
  <div class="suggestion-banner">
    <div class="suggestion-content">
      <span class="suggestion-icon">🔬</span>
      <div class="suggestion-text">
        <strong>Ready to experience what you're building?</strong>
        <p>Test your consciousness integrations in our interactive playground</p>
      </div>
      <a href="https://lukhas.app" class="suggestion-cta">Try lukhas.app</a>
    </div>
  </div>
</div>
```

---

## 🎨 Adaptive Navigation Styling

### **CSS Framework for Constellation Navigation**
```css
/* Base Constellation Styles */
.constellation-primary {
  position: relative;
  background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 32px;
}

.star-group {
  display: flex;
  gap: 16px;
  align-items: center;
  margin-bottom: 16px;
}

.star {
  font-size: 24px;
  padding: 12px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

.star:hover {
  transform: scale(1.1);
  background: rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.star.active {
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
  box-shadow: 0 8px 32px rgba(79, 70, 229, 0.4);
}

/* Domain-Specific Color Schemes */
.domain-link.dream-quantum {
  background: linear-gradient(135deg, #1e1b4b 0%, #581c87 100%);
  color: #e0e7ff;
}

.domain-link.guardian-identity {
  background: linear-gradient(135deg, #164e63 0%, #155e75 100%);
  color: #cffafe;
}

.domain-link.vision-bio {
  background: linear-gradient(135deg, #065f46 0%, #047857 100%);
  color: #d1fae5;
}

.domain-link.ethics-guardian {
  background: linear-gradient(135deg, #7c2d12 0%, #9a3412 100%);
  color: #fed7aa;
}

/* Responsive Navigation */
@media (max-width: 768px) {
  .constellation-primary {
    padding: 16px;
  }
  
  .star-group {
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .star {
    font-size: 20px;
    padding: 8px;
  }
  
  .domain-navigator .category {
    margin-bottom: 24px;
  }
}
```

---

## 🌐 JavaScript Navigation Intelligence

### **Context-Aware Navigation**
```javascript
class ConstellationNavigation {
  constructor() {
    this.currentDomain = this.detectCurrentDomain();
    this.userContext = this.loadUserContext();
    this.initializeNavigation();
  }
  
  detectCurrentDomain() {
    const hostname = window.location.hostname;
    return hostname.replace('www.', '');
  }
  
  initializeNavigation() {
    this.setupStarInteractions();
    this.generateContextualSuggestions();
    this.trackNavigationPatterns();
  }
  
  setupStarInteractions() {
    document.querySelectorAll('.star').forEach(star => {
      star.addEventListener('click', (e) => {
        const domains = e.target.dataset.domains.split(',');
        this.showDomainOptions(domains, e.target);
      });
      
      star.addEventListener('mouseenter', (e) => {
        this.previewStarDomains(e.target);
      });
    });
  }
  
  generateContextualSuggestions() {
    const suggestions = this.getSmartSuggestions();
    this.displaySuggestions(suggestions);
  }
  
  getSmartSuggestions() {
    const flows = {
      'lukhas.ai': [
        { domain: 'lukhas.app', reason: 'Try building consciousness interfaces', confidence: 0.8 },
        { domain: 'lukhas.com', reason: 'Explore business applications', confidence: 0.6 }
      ],
      'lukhas.com': [
        { domain: 'lukhas.cloud', reason: 'Deploy at scale', confidence: 0.9 },
        { domain: 'lukhas.id', reason: 'Secure authentication', confidence: 0.7 }
      ],
      'lukhas.io': [
        { domain: 'lukhas.app', reason: 'Test your integrations', confidence: 0.8 },
        { domain: 'lukhas.dev', reason: 'Join the community', confidence: 0.6 }
      ]
    };
    
    return flows[this.currentDomain] || [];
  }
  
  displaySuggestions(suggestions) {
    const container = document.querySelector('.navigation-suggestions');
    if (!container || !suggestions.length) return;
    
    const topSuggestion = suggestions.sort((a, b) => b.confidence - a.confidence)[0];
    this.renderSuggestion(container, topSuggestion);
  }
  
  trackNavigationPatterns() {
    // Analytics for improving navigation suggestions
    const navigationEvent = {
      from: this.currentDomain,
      timestamp: Date.now(),
      context: this.userContext
    };
    
    // Send to analytics (implementation depends on analytics platform)
    this.recordNavigation(navigationEvent);
  }
}

// Initialize navigation system
document.addEventListener('DOMContentLoaded', () => {
  new ConstellationNavigation();
});
```

---

## 📱 Mobile Navigation Adaptations

### **Mobile-First Constellation Selector**
```html
<div class="mobile-constellation">
  <button class="constellation-toggle">
    <span class="current-star">🌙</span>
    <span class="domain-name">lukhas.ai</span>
    <span class="expand-icon">↓</span>
  </button>
  
  <div class="constellation-dropdown">
    <div class="star-grid">
      <div class="star-item" data-domains="lukhas.id">
        <span class="star">⚛️</span>
        <span class="label">Identity</span>
      </div>
      <div class="star-item" data-domains="lukhas.cloud,lukhas.team">
        <span class="star">✦</span>
        <span class="label">Memory</span>
      </div>
      <!-- Additional stars... -->
    </div>
    
    <div class="quick-domains">
      <a href="https://lukhas.ai" class="quick-domain active">
        <span class="domain">.ai</span>
        <span class="tagline">Dreaming Heart</span>
      </a>
      <a href="https://lukhas.com" class="quick-domain">
        <span class="domain">.com</span>
        <span class="tagline">Business Hub</span>
      </a>
      <!-- Additional domains... -->
    </div>
  </div>
</div>
```

---

## 🎯 Navigation Performance & Analytics

### **Navigation Success Metrics**
```javascript
const navigationMetrics = {
  crossDomainEngagement: {
    target: '>60% users visit 2+ domains per session',
    measurement: 'unique domains per session'
  },
  
  contextualSuggestionSuccess: {
    target: '>40% click-through on suggested domains',
    measurement: 'suggestions clicked / suggestions shown'
  },
  
  constellationAwareness: {
    target: '>80% users understand current star alignment',
    measurement: 'post-session constellation comprehension survey'
  },
  
  navigationEfficiency: {
    target: '<3 clicks to reach intended domain',
    measurement: 'average clicks from entry to target domain'
  }
};
```

---

## 🔮 Advanced Navigation Features

### **Personalized Constellation Views**
```javascript
class PersonalizedNavigation extends ConstellationNavigation {
  constructor() {
    super();
    this.userProfile = this.loadUserProfile();
    this.adaptNavigationToUser();
  }
  
  adaptNavigationToUser() {
    const userType = this.detectUserType();
    const customization = this.getNavigationCustomization(userType);
    this.applyCustomization(customization);
  }
  
  detectUserType() {
    // Analyze user behavior patterns
    const patterns = {
      developer: this.userProfile.domains.includes('lukhas.io') && this.userProfile.timeSpent['lukhas.dev'] > 300,
      business: this.userProfile.domains.includes('lukhas.com') && this.userProfile.interests.includes('enterprise'),
      researcher: this.userProfile.domains.includes('lukhas.lab') || this.userProfile.domains.includes('lukhas.xyz'),
      explorer: this.userProfile.domains.length > 5 && this.userProfile.averageSessionDuration > 600
    };
    
    return Object.keys(patterns).find(type => patterns[type]) || 'general';
  }
  
  getNavigationCustomization(userType) {
    const customizations = {
      developer: {
        priorityDomains: ['lukhas.io', 'lukhas.dev', 'lukhas.app'],
        hiddenCategories: [],
        additionalSuggestions: ['lukhas.xyz', 'lukhas.lab']
      },
      business: {
        priorityDomains: ['lukhas.com', 'lukhas.cloud', 'lukhas.team'],
        hiddenCategories: ['research'],
        additionalSuggestions: ['lukhas.store', 'lukhas.id']
      },
      researcher: {
        priorityDomains: ['lukhas.lab', 'lukhas.xyz', 'lukhas.ai'],
        hiddenCategories: [],
        additionalSuggestions: ['lukhas.dev', 'lukhas.io']
      }
    };
    
    return customizations[userType] || customizations.general;
  }
}
```

---

This constellation navigation system creates a unified yet adaptive experience across all 13 LUKHAS domains, maintaining constellation awareness while respecting each domain's unique identity and user journey requirements.