# 🗺️ Sky Map Design Specification

**Interactive Constellation Navigation System**

---

## 🎯 Overview

The Sky Map is the visual manifestation of the LUKHAS Universe — an interactive constellation navigation system deployable across all domains. It transforms the 8-star vocabulary framework into a functional, beautiful interface.

---

## 🌟 Core Components

### 1. Constellation Grid

```css
.constellation-grid {
  position: relative;
  width: 100vw;
  height: 100vh;
  background: radial-gradient(circle, #000814 0%, #001d3d 100%);
  overflow: hidden;
}
```

### 2. Star Positioning

**Center Cluster** (Identity, Guardian, Ethics)
```css
.center-cluster {
  position: absolute;
  top: 50%;
  left: 50%; 
  transform: translate(-50%, -50%);
  display: grid;
  grid-template-columns: repeat(3, 80px);
  gap: 40px;
}
```

**Orbital Rings**
```css
.orbit-ring {
  position: absolute;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.orbit-1 { width: 300px; height: 300px; }  /* Memory, Dream */
.orbit-2 { width: 500px; height: 500px; }  /* Vision, Bio */ 
.orbit-3 { width: 700px; height: 700px; }  /* Quantum */
```

### 3. Star Elements

```jsx
const Star = ({ name, position, constellation, domains }) => (
  <div 
    className={`star star-${name.toLowerCase()}`}
    style={{ 
      position: 'absolute',
      top: position.y,
      left: position.x,
      transform: 'translate(-50%, -50%)'
    }}
    onMouseEnter={() => highlightConstellation(constellation)}
    onClick={() => revealDomains(domains)}
  >
    <div className="star-glyph">{getGlyph(name)}</div>
    <div className="star-label">{name}</div>
    <div className="star-pulse"></div>
  </div>
);
```

---

## 🎨 Visual Design System

### Star Glyphs
- **⚛️ Identity**: Atomic symbol with orbital rings
- **✦ Memory**: Multi-pointed star with trailing light
- **🔬 Vision**: Lens/aperture symbol with focus rays  
- **🌱 Bio**: Organic spiral with growth tendrils
- **🌙 Dream**: Crescent with drifting particles
- **⚖️ Ethics**: Balance scales with geometric precision
- **🛡️ Guardian**: Shield with watchtower silhouette
- **⚛️ Quantum**: Overlapping probability circles

### Color Palette

```css
:root {
  /* Base Cosmos */
  --cosmos-deep: #000814;
  --cosmos-mid: #001d3d;
  --cosmos-light: #003566;
  
  /* Star Colors */
  --star-identity: #ffd60a;     /* Golden anchor */
  --star-memory: #003566;       /* Deep blue trails */
  --star-vision: #0077b6;       /* Bright blue horizon */
  --star-bio: #008000;          /* Living green */
  --star-dream: #7209b7;        /* Purple drift */
  --star-ethics: #f77f00;       /* Orange accountability */
  --star-guardian: #dc2f02;     /* Red protection */
  --star-quantum: #6a4c93;      /* Violet uncertainty */
  
  /* Interaction States */
  --glow-hover: rgba(255, 214, 10, 0.6);
  --glow-active: rgba(255, 214, 10, 0.9);
  --connection-line: rgba(255, 255, 255, 0.3);
}
```

### Animation System

```css
@keyframes starPulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.1); opacity: 0.8; }
}

@keyframes constellationGlow {
  from { opacity: 0.3; }
  to { opacity: 0.8; }
}

@keyframes orbitRotate {
  from { transform: translate(-50%, -50%) rotate(0deg); }
  to { transform: translate(-50%, -50%) rotate(360deg); }
}
```

---

## 🔧 Interactive Behaviors

### 1. Star Hover States

```javascript
const handleStarHover = (starName) => {
  // Highlight constellation connections
  document.querySelectorAll('.connection-line').forEach(line => {
    if (line.dataset.connects.includes(starName)) {
      line.classList.add('highlighted');
    }
  });
  
  // Show domain preview
  showDomainPreview(starName);
  
  // Pulse related orbit
  const orbit = getOrbitForStar(starName);
  orbit.classList.add('pulsing');
};
```

### 2. Star Click Actions

```javascript
const handleStarClick = (starName, domains) => {
  // Expand star details panel
  showStarPanel({
    name: starName,
    vocabulary: getVocabulary(starName),
    domains: domains,
    description: getStarDescription(starName)
  });
  
  // Highlight associated domains
  domains.forEach(domain => {
    const domainNode = document.querySelector(`[data-domain="${domain}"]`);
    domainNode.classList.add('highlighted');
  });
};
```

### 3. Domain Navigation

```javascript
const navigateToDomain = (domain) => {
  // Smooth transition animation
  const targetUrl = `https://${domain}`;
  
  // Show navigation preview
  showNavigationPreview(domain);
  
  // Delayed redirect for animation
  setTimeout(() => {
    window.location.href = targetUrl;
  }, 800);
};
```

---

## 🪐 Domain Planet System

### Planet Visualization

```jsx
const Planet = ({ domain, star, size, orbit }) => (
  <div 
    className={`planet planet-${domain.replace('.', '-')}`}
    data-domain={domain}
    style={{
      position: 'absolute',
      width: `${size}px`,
      height: `${size}px`,
      background: `radial-gradient(circle, var(--star-${star}), transparent)`,
      borderRadius: '50%',
      transform: `rotate(${orbit.angle}deg) translateX(${orbit.radius}px)`
    }}
    onClick={() => navigateToDomain(domain)}
  >
    <div className="planet-label">{domain}</div>
  </div>
);
```

### Orbital Mechanics

```javascript
const orbitSpeeds = {
  'orbit-1': 60000,  // Memory, Dream - 1 minute
  'orbit-2': 90000,  // Vision, Bio - 1.5 minutes  
  'orbit-3': 120000  // Quantum - 2 minutes
};

const animateOrbits = () => {
  Object.entries(orbitSpeeds).forEach(([orbit, duration]) => {
    const planets = document.querySelectorAll(`.${orbit} .planet`);
    planets.forEach(planet => {
      planet.style.animation = `orbitRotate ${duration}ms linear infinite`;
    });
  });
};
```

---

## 📱 Responsive Design

### Mobile Sky Map

```css
@media (max-width: 768px) {
  .constellation-grid {
    height: 100vh;
    overflow-y: scroll;
  }
  
  .orbit-ring {
    position: relative;
    margin: 40px auto;
    transform: none;
  }
  
  .center-cluster {
    position: relative;
    transform: none;
    margin: 60px auto;
  }
}
```

### Touch Interactions

```javascript
const handleTouchInteractions = () => {
  // Touch-friendly star selection
  document.querySelectorAll('.star').forEach(star => {
    star.addEventListener('touchstart', (e) => {
      e.preventDefault();
      handleStarClick(star.dataset.name);
    });
  });
  
  // Swipe navigation between constellations  
  let touchStartX = 0;
  document.addEventListener('touchstart', e => {
    touchStartX = e.touches[0].clientX;
  });
  
  document.addEventListener('touchend', e => {
    const touchEndX = e.changedTouches[0].clientX;
    const swipeDistance = touchEndX - touchStartX;
    
    if (Math.abs(swipeDistance) > 100) {
      navigateConstellation(swipeDistance > 0 ? 'next' : 'prev');
    }
  });
};
```

---

## 🌓 Sky Modes

### Dark Mode (Default)

```css
.sky-dark {
  --background: radial-gradient(circle, #000814 0%, #001d3d 100%);
  --star-glow: rgba(255, 255, 255, 0.8);
  --text-primary: #ffffff;
  --constellation-line: rgba(255, 255, 255, 0.3);
}
```

### Light Mode (Cosmic Parchment)

```css
.sky-light {
  --background: linear-gradient(135deg, #f8f1e0 0%, #e6d7c2 100%);
  --star-glow: rgba(0, 0, 0, 0.6);
  --text-primary: #2c1810;
  --constellation-line: rgba(139, 124, 101, 0.4);
}
```

### Time-Based Transitions

```javascript
const updateSkyMode = () => {
  const hour = new Date().getHours();
  const body = document.body;
  
  if (hour >= 6 && hour < 18) {
    body.classList.remove('sky-dark');
    body.classList.add('sky-light');
  } else {
    body.classList.remove('sky-light'); 
    body.classList.add('sky-dark');
  }
};

// Update every hour
setInterval(updateSkyMode, 3600000);
```

---

## 🔗 Cross-Domain Integration

### Shared Constellation Header

```jsx
const ConstellationHeader = () => (
  <header className="constellation-nav">
    <div className="mini-constellation">
      {stars.map(star => (
        <button 
          key={star.name}
          className="nav-star"
          onClick={() => navigateToStar(star)}
        >
          {star.glyph}
        </button>
      ))}
    </div>
    <button 
      className="sky-map-return"
      onClick={() => openSkyMap()}
    >
      Return to Sky Map
    </button>
  </header>
);
```

### Universal Sky Map Modal

```jsx
const SkyMapModal = ({ isOpen, onClose }) => (
  <div className={`sky-map-modal ${isOpen ? 'active' : ''}`}>
    <div className="modal-background" onClick={onClose} />
    <div className="sky-map-container">
      <ConstellationGrid interactive={true} />
      <button className="close-modal" onClick={onClose}>×</button>
    </div>
  </div>
);
```

---

## 📊 Analytics Integration

### Constellation Navigation Tracking

```javascript
const trackConstellationNavigation = (action, star, domain = null) => {
  analytics.track('constellation_navigation', {
    action: action,        // 'hover', 'click', 'navigate'
    star: star,           // Star name
    domain: domain,       // Target domain if applicable
    timestamp: Date.now(),
    user_path: getUserPath()
  });
};
```

### Performance Metrics

```javascript
const constellationMetrics = {
  loadTime: 0,
  interactionCount: 0,
  navigationSuccess: 0,
  averageTimeToNavigation: 0
};

const measurePerformance = () => {
  // Track constellation load time
  const loadStart = performance.mark('constellation-start');
  // ... constellation initialization
  const loadEnd = performance.mark('constellation-end');
  
  constellationMetrics.loadTime = performance.measure(
    'constellation-load', 
    'constellation-start', 
    'constellation-end'
  ).duration;
};
```

---

## ✅ Implementation Checklist

### Phase 1: Core Sky Map
- [ ] Create constellation grid layout
- [ ] Implement 8-star positioning system
- [ ] Add orbital ring visualization
- [ ] Design star glyph system
- [ ] Implement basic hover/click interactions

### Phase 2: Domain Planets
- [ ] Add planet nodes for each domain
- [ ] Implement orbital animations
- [ ] Create domain navigation system
- [ ] Add planet size/importance weighting

### Phase 3: Interactive Features
- [ ] Star details panels
- [ ] Domain preview system
- [ ] Constellation line connections
- [ ] Touch/mobile interactions

### Phase 4: Integration & Polish
- [ ] Cross-domain header integration
- [ ] Sky mode switching
- [ ] Performance optimization
- [ ] Analytics integration
- [ ] Accessibility features

---

## 🎊 Final Result

**A fully interactive constellation navigation system that transforms your brand metaphor into a functional, beautiful interface.**

- **8 clickable stars** with hover states and detail panels
- **Domain planets** orbiting their constellation stars  
- **Smooth animations** and transitions between states
- **Mobile-responsive** design with touch interactions
- **Cross-domain integration** with shared navigation
- **Sky modes** for different contexts and times
- **Analytics tracking** for navigation optimization

🌌 **Your brand universe becomes your user interface.** ✦

---

*Technical specification ready for development team implementation*  
*"Navigate by starlight, land on planets"*
