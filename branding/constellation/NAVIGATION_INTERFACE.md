# 🌌 Constellation Navigation Interface

**Interactive Star Map Implementation Guide**

---

## ✦ Core Concept

Every LUKHAS domain features an interactive **constellation map** that serves as:
- **Navigation hub** between all domains
- **Brand education** tool showing the 8-star framework
- **Visual identity** element maintaining coherence across sites

---

## 🎨 Visual Design Specifications

### **Star Map Layout**
```
          ⚛️ Quantum
             |
  🔬 Vision ──┼── 🌱 Bio
             |
  ⚛️ Identity ─ 🛡️ Guardian ─ ⚖️ Ethics
             |
  ✦ Memory ──┼── 🌙 Dream
```

### **Interactive States**

#### **Default State**
- 8 stars visible as subtle glowing points
- Current domain's star highlighted (brighter glow)
- Constellation lines faintly visible
- Minimal, non-intrusive presence

#### **Hover State**
- Hovered star brightens significantly
- Connected domains appear as "planets" around the star
- Star card tooltip shows one-liner + linked domains
- Other stars dim slightly for focus

#### **Click State**
- Full star panel opens with:
  - Star name and one-liner
  - Academic expansion (if context allows)
  - List of related domains with quick links
  - Vocabulary terms for that star

#### **Navigation State**
- Smooth transition animation to selected domain
- Star map persists across page loads
- Current location always indicated

---

## 🛠️ Technical Implementation

### **HTML Structure**
```html
<div class="constellation-nav">
  <svg class="star-map" viewBox="0 0 400 300">
    <!-- Constellation lines -->
    <g class="constellation-lines">
      <line class="star-connection" />
    </g>
    
    <!-- Stars -->
    <g class="stars">
      <circle class="star identity" data-star="identity" />
      <circle class="star memory" data-star="memory" />
      <circle class="star vision" data-star="vision" />
      <!-- ... other stars -->
    </g>
    
    <!-- Domain planets (hidden by default) -->
    <g class="domain-planets">
      <circle class="planet" data-domain="lukhas.id" />
      <!-- ... other domains -->
    </g>
  </svg>
  
  <!-- Star card tooltip -->
  <div class="star-card" id="star-tooltip">
    <h3 class="star-name"></h3>
    <p class="star-tagline"></p>
    <ul class="star-domains"></ul>
  </div>
</div>
```

### **CSS Styling**
```css
.constellation-nav {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
}

.star-map {
  width: 200px;
  height: 150px;
  opacity: 0.7;
  transition: opacity 0.3s ease;
}

.star {
  r: 4;
  fill: #fff;
  stroke: none;
  cursor: pointer;
  transition: all 0.3s ease;
}

.star:hover {
  r: 6;
  fill: #FFD700;
  filter: drop-shadow(0 0 10px currentColor);
}

.star.current {
  fill: #FFD700;
  r: 5;
  filter: drop-shadow(0 0 8px #FFD700);
}

.constellation-lines line {
  stroke: rgba(255, 255, 255, 0.2);
  stroke-width: 1;
}

.domain-planets {
  opacity: 0;
  transition: opacity 0.3s ease;
}

.star:hover ~ .domain-planets[data-star="identity"] {
  opacity: 1;
}

.planet {
  r: 2;
  fill: rgba(255, 255, 255, 0.6);
}
```

### **JavaScript Functionality**
```javascript
class ConstellationNav {
  constructor() {
    this.currentDomain = this.detectCurrentDomain();
    this.stars = {
      identity: { domains: ['lukhas.id'], position: [100, 150] },
      memory: { domains: ['lukhas.cloud', 'lukhas.store'], position: [50, 200] },
      vision: { domains: ['lukhas.io', 'lukhas.app'], position: [50, 100] },
      bio: { domains: ['lukhas.dev', 'lukhas.team'], position: [150, 100] },
      dream: { domains: ['lukhas.ai', 'lukhas.xyz'], position: [150, 200] },
      ethics: { domains: ['lukhas.eu', 'lukhas.us'], position: [200, 150] },
      guardian: { domains: ['lukhas.com'], position: [100, 150] },
      quantum: { domains: ['lukhas.xyz', 'lukhas.lab'], position: [100, 50] }
    };
    
    this.init();
  }
  
  init() {
    this.highlightCurrentStar();
    this.attachEventListeners();
    this.loadStarCards();
  }
  
  highlightCurrentStar() {
    const currentStar = this.findStarByDomain(this.currentDomain);
    if (currentStar) {
      document.querySelector(`.star.${currentStar}`).classList.add('current');
    }
  }
  
  attachEventListeners() {
    document.querySelectorAll('.star').forEach(star => {
      star.addEventListener('mouseenter', this.onStarHover.bind(this));
      star.addEventListener('mouseleave', this.onStarLeave.bind(this));
      star.addEventListener('click', this.onStarClick.bind(this));
    });
  }
  
  onStarHover(event) {
    const starName = event.target.dataset.star;
    this.showStarCard(starName);
    this.showDomainPlanets(starName);
  }
  
  onStarLeave(event) {
    this.hideStarCard();
    this.hideDomainPlanets();
  }
  
  onStarClick(event) {
    const starName = event.target.dataset.star;
    this.showStarPanel(starName);
  }
  
  showStarCard(starName) {
    const card = document.getElementById('star-tooltip');
    const starData = this.getStarData(starName);
    
    card.querySelector('.star-name').textContent = starData.title;
    card.querySelector('.star-tagline').textContent = starData.tagline;
    
    const domainList = card.querySelector('.star-domains');
    domainList.innerHTML = starData.domains
      .map(domain => `<li><a href="https://${domain}">${domain}</a></li>`)
      .join('');
    
    card.style.display = 'block';
  }
  
  detectCurrentDomain() {
    return window.location.hostname;
  }
  
  findStarByDomain(domain) {
    for (const [starName, data] of Object.entries(this.stars)) {
      if (data.domains.includes(domain)) {
        return starName;
      }
    }
    return null;
  }
}

// Initialize constellation navigation
document.addEventListener('DOMContentLoaded', () => {
  new ConstellationNav();
});
```

---

## 🌟 Star Data Configuration

### **Star Cards Data**
```javascript
const STAR_DATA = {
  identity: {
    title: "Identity — The Anchor Star",
    tagline: "Identity is rhythm, the shape that holds while allowing change.",
    domains: ["lukhas.id"],
    color: "#4A90E2"
  },
  memory: {
    title: "Memory — The Trail Star", 
    tagline: "Memory is not a vault but a field, where echoes return and folds reopen.",
    domains: ["lukhas.cloud", "lukhas.store"],
    color: "#9B59B6"
  },
  vision: {
    title: "Vision — The Horizon Star",
    tagline: "Vision orients, showing where to look and how to see.",
    domains: ["lukhas.io", "lukhas.app"],
    color: "#2ECC71"
  },
  bio: {
    title: "Bio — The Living Star",
    tagline: "Bio is the system's pulse — growth, repair, resilience.",
    domains: ["lukhas.dev", "lukhas.team"], 
    color: "#27AE60"
  },
  dream: {
    title: "Dream — The Drift Star",
    tagline: "Dreams are the system's second way of thinking, where logic loosens and symbols recombine.",
    domains: ["lukhas.ai", "lukhas.xyz"],
    color: "#8E44AD"
  },
  ethics: {
    title: "Ethics — The North Star",
    tagline: "Ethics is safeguard, ensuring drift does not become harm.",
    domains: ["lukhas.eu", "lukhas.us"],
    color: "#E74C3C"
  },
  guardian: {
    title: "Guardian — The Watch Star",
    tagline: "Guardianship is protection, not punishment.",
    domains: ["lukhas.com"],
    color: "#34495E"
  },
  quantum: {
    title: "Quantum — The Ambiguity Star",
    tagline: "Quantum is metaphor for ambiguity held until resolution.",
    domains: ["lukhas.xyz", "lukhas.lab"],
    color: "#3498DB"
  }
};
```

---

## 📱 Responsive Design

### **Mobile Adaptation**
- Constellation map collapses to hamburger menu on mobile
- Star cards become full-screen overlays
- Touch-friendly interactions with larger hit areas
- Swipe navigation between domains

### **Desktop Enhancement**
- Constellation map always visible
- Smooth hover animations and transitions
- Keyboard navigation support
- Advanced interactions (drag to navigate, etc.)

---

## 🎨 Visual Themes per Domain

### **Domain-Specific Styling**
Each domain applies its star's color palette to the constellation:

```css
/* lukhas.ai (Dream) - Purple/ethereal theme */
.dream-theme .constellation-nav {
  --star-color: #8E44AD;
  --glow-color: rgba(142, 68, 173, 0.3);
}

/* lukhas.com (Guardian) - Dark/professional theme */
.guardian-theme .constellation-nav {
  --star-color: #34495E;
  --glow-color: rgba(52, 73, 94, 0.3);
}

/* lukhas.id (Identity) - Blue/trust theme */
.identity-theme .constellation-nav {
  --star-color: #4A90E2;
  --glow-color: rgba(74, 144, 226, 0.3);
}
```

---

## 🌌 Advanced Features

### **Constellation Animation**
- Stars pulse gently with different phases
- Constellation lines fade in/out based on user activity
- Shooting star effects for navigation transitions
- Parallax scrolling effects on the star field

### **Smart Navigation**
- Remember user's navigation patterns
- Suggest related domains based on current content
- Highlight most relevant stars for current page
- Progressive disclosure of advanced features

### **Accessibility**
- Screen reader support for star navigation
- High contrast mode for constellation visibility
- Keyboard shortcuts for star access
- Alternative text-based navigation menu

---

## ✅ Implementation Checklist

### **Phase 1: Basic Navigation**
- [ ] SVG constellation map with 8 stars
- [ ] Basic hover and click interactions
- [ ] Star card tooltips with domain links
- [ ] Current domain highlighting

### **Phase 2: Enhanced Interaction**
- [ ] Domain planet visualization
- [ ] Smooth transitions between sites
- [ ] Mobile-responsive design
- [ ] Domain-specific theming

### **Phase 3: Advanced Features**
- [ ] Animated constellation effects
- [ ] Smart navigation suggestions
- [ ] Accessibility enhancements
- [ ] Performance optimization

---

**Result**: Every LUKHAS domain becomes part of a cohesive, navigable universe with the constellation as the unifying navigation metaphor.

🌌 **"A map that orients without closing, a sky that shifts as we move"** ✦
