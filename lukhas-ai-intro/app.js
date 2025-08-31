// LUKHΛS ΛI - Sophisticated Intro Experience
// Fixed version addressing all critical issues

class LuxuryIntroExperience {
  constructor() {
    this.currentPhase = 0;
    this.totalPhases = 5;
    this.phaseDurations = [2500, 3500, 4000, 3000, 2000]; // milliseconds
    this.isSkipped = false;
    this.particles = [];
    this.canvas = null;
    this.ctx = null;
    this.phaseTimer = null;

    // Store reference globally for debugging
    window.introExperience = this;

    this.init();
  }

  init() {
    console.log('Initializing LUKHΛS ΛI intro experience...');
    this.setupCanvas();
    this.setupEventListeners();
    this.setupProgressBar();
    this.startIntroSequence();
    this.createParticleSystem();
    this.animateParticles();
  }

  setupCanvas() {
    this.canvas = document.getElementById('particleCanvas');
    if (!this.canvas) {
      console.error('Particle canvas not found');
      return;
    }

    this.ctx = this.canvas.getContext('2d');
    this.resizeCanvas();

    // Handle canvas resize
    window.addEventListener('resize', () => this.resizeCanvas());
  }

  resizeCanvas() {
    if (!this.canvas) return;
    this.canvas.width = window.innerWidth;
    this.canvas.height = window.innerHeight;
  }

  setupProgressBar() {
    // Create the CSS for progress bar animation
    const progressStyle = document.createElement('style');
    progressStyle.id = 'progress-style';
    progressStyle.textContent = `
      .progress-bar::before {
        content: '';
        display: block;
        width: 0;
        height: 100%;
        background: linear-gradient(90deg, var(--accent-amber), var(--rich-gold));
        border-radius: 1px;
        transition: width var(--transition-smooth);
        box-shadow: 0 0 10px var(--soft-glow);
      }
    `;
    document.head.appendChild(progressStyle);

    // Initialize progress
    this.updateProgress(0);
  }

  setupEventListeners() {
    // Skip intro button
    const skipBtn = document.getElementById('skipIntro');
    if (skipBtn) {
      skipBtn.addEventListener('click', (e) => {
        e.preventDefault();
        console.log('Skip intro clicked');
        this.skipIntro();
      });
    } else {
      console.error('Skip intro button not found');
    }

    // Enter experience button  
    const enterBtn = document.getElementById('enterBtn');
    if (enterBtn) {
      enterBtn.addEventListener('click', (e) => {
        e.preventDefault();
        console.log('Enter experience clicked');
        this.enterExperience();
      });
    } else {
      console.error('Enter experience button not found');
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' || e.key === ' ') {
        this.skipIntro();
      } else if (e.key === 'Enter' && this.currentPhase === 4) {
        this.enterExperience();
      }
    });

    // Prevent context menu for luxury experience
    document.addEventListener('contextmenu', (e) => e.preventDefault());
  }

  startIntroSequence() {
    console.log('Starting intro sequence...');

    // Ensure first phase is active
    const firstPhase = document.getElementById('phase1');
    if (firstPhase) {
      firstPhase.classList.add('active');
    }

    // Start letter animation
    setTimeout(() => {
      this.animateLetters();
    }, 500);

    // Schedule phase transitions
    this.schedulePhaseTransitions();
  }

  animateLetters() {
    const letters = document.querySelectorAll('.letter, .lambda, .space');
    console.log(`Animating ${letters.length} letters`);

    letters.forEach((letter, index) => {
      const delay = parseInt(letter.dataset.delay) || index * 100;
      setTimeout(() => {
        letter.style.opacity = '1';
        letter.style.transform = 'translateY(0) scale(1)';
      }, delay);
    });
  }

  schedulePhaseTransitions() {
    if (this.isSkipped) return;

    console.log('Scheduling phase transitions...');

    // Clear any existing timer
    if (this.phaseTimer) {
      clearTimeout(this.phaseTimer);
    }

    // Schedule transitions for all phases
    let cumulativeDelay = this.phaseDurations[0]; // Start after first phase duration

    for (let i = 1; i < this.totalPhases; i++) {
      setTimeout(() => {
        if (!this.isSkipped) {
          console.log(`Transitioning to phase ${i + 1}`);
          this.transitionToPhase(i);
        }
      }, cumulativeDelay);

      if (i < this.totalPhases - 1) {
        cumulativeDelay += this.phaseDurations[i];
      }
    }
  }

  transitionToPhase(phaseIndex) {
    if (this.isSkipped || phaseIndex >= this.totalPhases) return;

    console.log(`Transitioning to phase ${phaseIndex + 1}`);

    // Update progress first
    this.updateProgress(phaseIndex);

    // Hide current phase
    const currentPhase = document.getElementById(`phase${this.currentPhase + 1}`);
    if (currentPhase) {
      currentPhase.classList.remove('active');
    }

    // Show new phase after brief delay
    setTimeout(() => {
      const newPhase = document.getElementById(`phase${phaseIndex + 1}`);
      if (newPhase) {
        newPhase.classList.add('active');
        console.log(`Phase ${phaseIndex + 1} now active`);

        // Execute phase-specific animations
        this.executePhaseSpecificAnimations(phaseIndex);
      } else {
        console.error(`Phase ${phaseIndex + 1} element not found`);
      }
    }, 300);

    this.currentPhase = phaseIndex;
  }

  executePhaseSpecificAnimations(phaseIndex) {
    console.log(`Executing animations for phase ${phaseIndex + 1}`);

    switch (phaseIndex) {
      case 1: // Welcome phase
        this.createWelcomeEffects();
        break;
      case 2: // Philosophy phase
        this.createPhilosophyEffects();
        break;
      case 3: // Constellation phase
        setTimeout(() => this.animateConstellation(), 500);
        break;
      case 4: // Enter phase
        this.createEnterEffects();
        break;
    }
  }

  createWelcomeEffects() {
    console.log('Creating welcome effects');
    // Add welcome-specific particle burst
    this.createParticleBurst(window.innerWidth / 2, window.innerHeight / 2, 20);
  }

  createPhilosophyEffects() {
    console.log('Creating philosophy effects');
    // Animate ambient shapes
    const shapes = document.querySelectorAll('.shape');
    shapes.forEach((shape, index) => {
      setTimeout(() => {
        shape.style.opacity = '0.3';
        shape.style.animation = `shapeFloat 8s ease-in-out infinite`;
      }, index * 300);
    });
  }

  animateConstellation() {
    console.log('Animating constellation');

    // Stars appear first
    const stars = document.querySelectorAll('.star');
    console.log(`Found ${stars.length} stars`);

    stars.forEach((star, index) => {
      setTimeout(() => {
        star.style.opacity = '1';
        star.style.transform = 'scale(1)';
      }, index * 300);
    });

    // Lines connect after stars appear
    const lines = document.querySelectorAll('.line');
    console.log(`Found ${lines.length} lines`);

    setTimeout(() => {
      lines.forEach((line, index) => {
        setTimeout(() => {
          line.style.opacity = '0.8';
        }, index * 200);
      });
    }, stars.length * 300 + 500);

    // Add constellation glow effect
    setTimeout(() => {
      this.addConstellationGlow();
    }, (stars.length * 300) + (lines.length * 200) + 1000);
  }

  addConstellationGlow() {
    const svg = document.querySelector('.constellation-svg');
    if (svg) {
      svg.style.filter = 'drop-shadow(0 0 20px rgba(127, 233, 255, 0.4))';
    }
  }

  createEnterEffects() {
    console.log('Creating enter effects');
    // Ensure enter button is visible and functional
    const enterBtn = document.getElementById('enterBtn');
    if (enterBtn) {
      enterBtn.style.opacity = '1';
      enterBtn.style.pointerEvents = 'all';
    }
  }

  updateProgress(phaseIndex) {
    console.log(`Updating progress to phase ${phaseIndex + 1}`);

    // Update progress bar width
    const progressPercent = ((phaseIndex + 1) / this.totalPhases) * 100;

    // Find progress bar and update it
    const progressBar = document.querySelector('.progress-bar');
    if (progressBar) {
      // Use CSS custom property for smooth animation
      document.documentElement.style.setProperty('--progress-width', `${progressPercent}%`);

      // Also directly update the pseudo-element via style injection
      const existingStyle = document.getElementById('progress-style');
      if (existingStyle) {
        existingStyle.textContent = `
          .progress-bar::before {
            content: '';
            display: block;
            width: ${progressPercent}%;
            height: 100%;
            background: linear-gradient(90deg, var(--accent-amber), var(--rich-gold));
            border-radius: 1px;
            transition: width var(--transition-smooth);
            box-shadow: 0 0 10px var(--soft-glow);
          }
        `;
      }
    }

    // Update progress dots
    const dots = document.querySelectorAll('.dot');
    dots.forEach((dot, index) => {
      if (index <= phaseIndex) {
        dot.classList.add('active');
      } else {
        dot.classList.remove('active');
      }
    });
  }

  skipIntro() {
    console.log('Skipping intro...');

    if (this.isSkipped) return;

    this.isSkipped = true;

    // Clear any timers
    if (this.phaseTimer) {
      clearTimeout(this.phaseTimer);
    }

    // Hide all phases
    const allPhases = document.querySelectorAll('.intro-phase');
    allPhases.forEach(phase => phase.classList.remove('active'));

    // Show final phase immediately
    const finalPhase = document.getElementById('phase5');
    if (finalPhase) {
      finalPhase.classList.add('active');
      console.log('Jumped to final phase');
    }

    this.currentPhase = 4;
    this.updateProgress(4);
    this.createEnterEffects();

    // Hide skip button
    const skipBtn = document.getElementById('skipIntro');
    if (skipBtn) {
      skipBtn.style.opacity = '0';
      skipBtn.style.pointerEvents = 'none';
    }
  }

  enterExperience() {
    console.log('Entering experience...');

    const transitionOverlay = document.getElementById('transitionOverlay');
    const enterBtn = document.getElementById('enterBtn');

    // Button click effect
    if (enterBtn) {
      enterBtn.style.transform = 'translateY(-1px) scale(0.98)';
      this.createButtonSparkles(enterBtn);
    }

    // Create magnificent particle explosion
    this.createParticleBurst(window.innerWidth / 2, window.innerHeight / 2, 50);

    setTimeout(() => {
      // Show transition overlay
      if (transitionOverlay) {
        transitionOverlay.classList.add('active');
        console.log('Transition overlay activated');
      }

      // Final sophisticated message
      setTimeout(() => {
        this.showFinalMessage();
      }, 1000);

    }, 500);
  }

  showFinalMessage() {
    console.log('Showing final message...');

    // Create elegant final transition message
    const finalMessage = document.createElement('div');
    finalMessage.style.cssText = `
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      z-index: 3000;
      text-align: center;
      color: #D4AF37;
      font-family: var(--font-primary);
      font-weight: 100;
      font-size: clamp(1.5rem, 4vw, 2.5rem);
      opacity: 0;
      animation: finalMessageReveal 2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    `;

    finalMessage.innerHTML = `
      <div style="margin-bottom: 1rem; font-size: 3rem;">✦</div>
      <div>Welcome to <span style="color: #7FE9FF;">LUKHΛS ΛI</span></div>
      <div style="font-size: 0.8em; opacity: 0.7; margin-top: 1rem; font-weight: 300;">
        Where consciousness and technology converge
      </div>
    `;

    // Add final message animation keyframe
    if (!document.getElementById('final-message-style')) {
      const finalStyle = document.createElement('style');
      finalStyle.id = 'final-message-style';
      finalStyle.textContent = `
        @keyframes finalMessageReveal {
          0% {
            opacity: 0;
            transform: translate(-50%, -50%) translateY(30px) scale(0.9);
          }
          100% {
            opacity: 1;
            transform: translate(-50%, -50%) translateY(0) scale(1);
          }
        }
      `;
      document.head.appendChild(finalStyle);
    }

    document.body.appendChild(finalMessage);

    // Auto-remove after showing
    setTimeout(() => {
      finalMessage.style.animation = 'finalMessageReveal 1s cubic-bezier(0.16, 1, 0.3, 1) reverse forwards';
      setTimeout(() => {
        if (finalMessage.parentNode) {
          finalMessage.parentNode.removeChild(finalMessage);
        }
      }, 1000);
    }, 3000);
  }

  createButtonSparkles(button) {
    const rect = button.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;

    console.log('Creating button sparkles');

    for (let i = 0; i < 15; i++) {
      setTimeout(() => {
        const sparkle = document.createElement('div');
        sparkle.style.cssText = `
          position: fixed;
          width: ${Math.random() * 4 + 2}px;
          height: ${Math.random() * 4 + 2}px;
          background: #7FE9FF;
          border-radius: 50%;
          pointer-events: none;
          z-index: 9999;
          left: ${centerX}px;
          top: ${centerY}px;
          box-shadow: 0 0 6px #7FE9FF;
        `;

        document.body.appendChild(sparkle);

        // Animate sparkle
        const angle = (i / 15) * Math.PI * 2;
        const distance = 80 + Math.random() * 40;

        const animation = sparkle.animate([
          {
            transform: 'translate(0, 0) scale(1)',
            opacity: 1
          },
          {
            transform: `translate(${Math.cos(angle) * distance}px, ${Math.sin(angle) * distance}px) scale(0)`,
            opacity: 0
          }
        ], {
          duration: 1200,
          easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)'
        });

        animation.onfinish = () => {
          if (sparkle.parentNode) {
            sparkle.parentNode.removeChild(sparkle);
          }
        };
      }, i * 50);
    }
  }

  // Sophisticated particle system
  createParticleSystem() {
    const particleCount = window.innerWidth < 768 ? 30 : 60;

    for (let i = 0; i < particleCount; i++) {
      this.particles.push({
        x: Math.random() * this.canvas.width,
        y: Math.random() * this.canvas.height,
        vx: (Math.random() - 0.5) * 0.5,
        vy: -Math.random() * 0.8 - 0.2,
        size: Math.random() * 2 + 0.5,
        opacity: Math.random() * 0.6 + 0.2,
        life: Math.random() * 200 + 100,
        maxLife: 200,
        color: this.getParticleColor()
      });
    }
  }

  getParticleColor() {
    const colors = [
      'rgba(127, 233, 255, 0.8)',  // Cyan glow
      'rgba(103, 232, 249, 0.6)',  // Light cyan
      'rgba(34, 211, 238, 0.7)',   // Teal-cyan
      'rgba(255, 255, 255, 0.4)'   // White
    ];
    return colors[Math.floor(Math.random() * colors.length)];
  }

  animateParticles() {
    if (!this.ctx || !this.canvas) return;

    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    // Update and draw particles
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const particle = this.particles[i];

      // Update position
      particle.x += particle.vx;
      particle.y += particle.vy;
      particle.life--;

      // Update opacity based on life
      particle.opacity = (particle.life / particle.maxLife) * 0.8;

      // Remove dead particles
      if (particle.life <= 0 || particle.y < -10) {
        this.particles.splice(i, 1);
        // Add new particle at bottom
        this.particles.push({
          x: Math.random() * this.canvas.width,
          y: this.canvas.height + 10,
          vx: (Math.random() - 0.5) * 0.5,
          vy: -Math.random() * 0.8 - 0.2,
          size: Math.random() * 2 + 0.5,
          opacity: Math.random() * 0.6 + 0.2,
          life: Math.random() * 200 + 100,
          maxLife: 200,
          color: this.getParticleColor()
        });
      }

      // Draw particle
      this.ctx.save();
      this.ctx.globalAlpha = particle.opacity;
      this.ctx.fillStyle = particle.color;
      this.ctx.shadowBlur = 10;
      this.ctx.shadowColor = particle.color;
      this.ctx.beginPath();
      this.ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
      this.ctx.fill();
      this.ctx.restore();
    }

    requestAnimationFrame(() => this.animateParticles());
  }

  createParticleBurst(x, y, count) {
    for (let i = 0; i < count; i++) {
      const angle = (i / count) * Math.PI * 2;
      const velocity = Math.random() * 3 + 1;

      this.particles.push({
        x: x,
        y: y,
        vx: Math.cos(angle) * velocity,
        vy: Math.sin(angle) * velocity,
        size: Math.random() * 3 + 1,
        opacity: 1,
        life: 60,
        maxLife: 60,
        color: this.getParticleColor()
      });
    }
  }
}

// Modern Blueprint Lambda Grid Implementation
(function(){
  // Wait for DOM to be ready before initializing the grid
  function initLambdaGrid() {
    const c = document.getElementById('lambdaGridCanvas');
    if (!c) {
      console.warn('Lambda Grid Canvas not found');
      return;
    }
    
    const ctx = c.getContext('2d');
    const DPR = Math.min(window.devicePixelRatio || 1, 2);

    // Performance and accessibility
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const motionScale = prefersReducedMotion ? 0.1 : 1;

    function resize(){
      c.width = Math.floor(innerWidth * DPR);
      c.height = Math.floor(innerHeight * DPR);
      c.style.width = innerWidth + 'px';
      c.style.height = innerHeight + 'px';
      ctx.setTransform(DPR,0,0,DPR,0,0);
    }
    resize(); addEventListener('resize', resize);

    const theme = getComputedStyle(document.documentElement);
    function color(name){ return theme.getPropertyValue(name).trim(); }

    // Modern grid configuration
    const grid = { 
      step: Math.max(24, Math.min(48, innerWidth / 50)), // Responsive grid size
      majorEvery: 5,
      fadeDistance: Math.min(innerWidth, innerHeight) * 0.4
    };

    // Enhanced corner elements with modern timing
    const corners = [
      {x: 80, y: 80, r: 32, speed: 0.08, phase: 0, type: 'precision'},
      {x: innerWidth-80, y: 80, r: 28, speed: -0.12, phase: Math.PI/3, type: 'quantum'},
      {x: 80, y: innerHeight-80, r: 36, speed: 0.06, phase: Math.PI/2, type: 'consciousness'},
      {x: innerWidth-80, y: innerHeight-80, r: 30, speed: -0.09, phase: Math.PI, type: 'synthesis'},
    ];

    // Easing functions for smooth animations
    const easing = {
      inOutCubic: t => t < 0.5 ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1,
      inOutQuart: t => t < 0.5 ? 8 * t * t * t * t : 1 - 8 * (--t) * t * t * t,
      inOutSine: t => -(Math.cos(Math.PI * t) - 1) / 2
    };

    function drawModernGrid(t){
      ctx.save();
      ctx.clearRect(0,0,innerWidth,innerHeight);

      // Sophisticated drift with multiple layers
      const primaryDrift = Math.sin(t * 0.0002) * 4 * motionScale;
      const secondaryDrift = Math.cos(t * 0.00015) * 2.5 * motionScale;
      const microDrift = Math.sin(t * 0.0008) * 0.8 * motionScale;

      // Dynamic vignette based on mouse position or center
      const vignetteStrength = 0.15;
      const centerX = innerWidth / 2;
      const centerY = innerHeight / 2;
      
      const gradient = ctx.createRadialGradient(
        centerX, centerY, Math.min(innerWidth, innerHeight) * 0.2,
        centerX, centerY, Math.max(innerWidth, innerHeight) * 0.8
      );
      gradient.addColorStop(0, 'transparent');
      gradient.addColorStop(0.7, `rgba(0,0,0,${vignetteStrength})`);
      gradient.addColorStop(1, `rgba(0,0,0,${vignetteStrength * 1.8})`);
      
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, innerWidth, innerHeight);

      // Adaptive grid opacity based on distance from center
      const drawGridLines = (offset, opacity, lineWidth = 1) => {
        ctx.lineWidth = lineWidth;
        ctx.globalAlpha = opacity;
        ctx.strokeStyle = color('--ink-subtle');

        for(let x = offset; x < innerWidth; x += grid.step){
          const distanceFromCenter = Math.abs(x - centerX);
          const fadeOpacity = Math.max(0.1, 1 - (distanceFromCenter / grid.fadeDistance));
          ctx.globalAlpha = opacity * fadeOpacity;
          
          ctx.beginPath();
          ctx.moveTo(x, 0);
          ctx.lineTo(x, innerHeight);
          ctx.stroke();
        }

        for(let y = offset; y < innerHeight; y += grid.step){
          const distanceFromCenter = Math.abs(y - centerY);
          const fadeOpacity = Math.max(0.1, 1 - (distanceFromCenter / grid.fadeDistance));
          ctx.globalAlpha = opacity * fadeOpacity;
          
          ctx.beginPath();
          ctx.moveTo(0, y);
          ctx.lineTo(innerWidth, y);
          ctx.stroke();
        }
      };

      // Multi-layer grid system
      drawGridLines((primaryDrift + microDrift) % grid.step, 0.15);
      drawGridLines((primaryDrift + secondaryDrift) % (grid.step * grid.majorEvery), 0.4, 1.5);

      // Measurement system with modern styling
      ctx.globalAlpha = 0.6;
      ctx.strokeStyle = color('--ink-subtle');
      ctx.lineWidth = 1;
      
      const tickSpacing = grid.step * 2;
      for(let x = 0; x < innerWidth; x += tickSpacing){
        const tickHeight = x % (tickSpacing * 3) === 0 ? 16 : 8;
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, tickHeight);
        ctx.stroke();
      }
      
      for(let y = 0; y < innerHeight; y += tickSpacing){
        const tickWidth = y % (tickSpacing * 3) === 0 ? 16 : 8;
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(tickWidth, y);
        ctx.stroke();
      }

      ctx.restore();
    }

    function drawModernLambda(t){
      const scale = Math.min(innerWidth, innerHeight) * 0.35;
      const cx = innerWidth / 2;
      const cy = innerHeight / 2 + scale * 0.05;
      
      // Breathing animation
      const breathe = 1 + Math.sin(t * 0.0008) * 0.02 * motionScale;
      const w = scale * breathe;
      const h = w * 1.1;
      const thickness = Math.max(1, w * 0.003);

      ctx.save();
      ctx.translate(cx, cy);
      
      // Sophisticated glow effect
      ctx.shadowColor = color('--glow');
      ctx.shadowBlur = 20;
      ctx.shadowOffsetX = 0;
      ctx.shadowOffsetY = 0;
      
      ctx.strokeStyle = color('--ink');
      ctx.lineWidth = thickness;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';
      ctx.globalAlpha = 0.9;

      // Main Lambda with smooth curves
      ctx.beginPath();
      ctx.moveTo(-w/2, h/2);
      ctx.lineTo(0, -h/2);
      ctx.lineTo(w/2, h/2);
      ctx.stroke();

      // Subtle construction geometry
      ctx.shadowBlur = 0;
      ctx.globalAlpha = 0.25;
      ctx.lineWidth = thickness * 0.5;
      ctx.setLineDash([8, 12]);

      const constructionOffset = easing.inOutSine((Math.sin(t * 0.0005) + 1) / 2) * 0.1;
      ctx.beginPath();
      ctx.moveTo(-w * (0.6 - constructionOffset), h * (0.15 + constructionOffset));
      ctx.lineTo(w * (0.6 - constructionOffset), h * (0.15 + constructionOffset));
      ctx.moveTo(-w * (0.35 + constructionOffset), -h * (0.2 - constructionOffset));
      ctx.lineTo(w * (0.35 + constructionOffset), -h * (0.2 - constructionOffset));
      ctx.stroke();

      ctx.setLineDash([]);
      ctx.restore();
    }

    function drawModernCorners(t){
      ctx.save();
      
      // Update corner positions for responsive design
      corners[1].x = innerWidth - 80;
      corners[3].x = innerWidth - 80;
      corners[2].y = innerHeight - 80;
      corners[3].y = innerHeight - 80;

      corners.forEach((corner, i) => {
        ctx.save();
        ctx.translate(corner.x, corner.y);
        
        const time = t * 0.001 * corner.speed * motionScale;
        const pulse = Math.sin(t * 0.002 + corner.phase) * 0.1 + 1;
        const rotation = time + corner.phase;
        
        // Outer ring with breathing effect
        const adjustedRadius = corner.r * pulse;
        ctx.beginPath();
        ctx.lineWidth = 1.5;
        ctx.globalAlpha = 0.4;
        ctx.strokeStyle = color('--ink-subtle');
        ctx.arc(0, 0, adjustedRadius, 0, Math.PI * 2);
        ctx.stroke();

        // Modern tick marks with varying opacity
        ctx.save();
        ctx.rotate(rotation);
        ctx.globalAlpha = 0.7;
        ctx.strokeStyle = color('--ink');
        ctx.lineWidth = 1;

        const tickCount = corner.type === 'precision' ? 72 : 60;
        for(let k = 0; k < tickCount; k++){
          const angle = (k / tickCount) * Math.PI * 2;
          const isMajor = k % (tickCount / 12) === 0;
          const isMinor = k % (tickCount / 24) === 0;
          
          let tickLength = isMajor ? 12 : (isMinor ? 8 : 4);
          let tickOpacity = isMajor ? 1 : (isMinor ? 0.7 : 0.4);
          
          ctx.globalAlpha = tickOpacity * 0.8;
          ctx.beginPath();
          const innerRadius = adjustedRadius - 3;
          const outerRadius = adjustedRadius - tickLength;
          ctx.moveTo(Math.cos(angle) * innerRadius, Math.sin(angle) * innerRadius);
          ctx.lineTo(Math.cos(angle) * outerRadius, Math.sin(angle) * outerRadius);
          ctx.stroke();
        }
        ctx.restore();

        // Sophisticated pointer with easing
        const pointerRotation = -rotation * 1.5;
        const pointerLength = adjustedRadius - 15;
        
        ctx.save();
        ctx.rotate(pointerRotation);
        ctx.globalAlpha = 0.9;
        ctx.strokeStyle = color('--ink');
        ctx.lineWidth = 2;
        ctx.lineCap = 'round';
        
        // Pointer with subtle taper
        ctx.beginPath();
        ctx.moveTo(0, 0);
        ctx.lineTo(pointerLength * 0.8, 0);
        ctx.lineWidth = 1;
        ctx.lineTo(pointerLength, 0);
        ctx.stroke();
        
        // Pointer tip
        ctx.beginPath();
        ctx.arc(pointerLength, 0, 1.5, 0, Math.PI * 2);
        ctx.fillStyle = color('--glow');
        ctx.fill();
        
        ctx.restore();
        ctx.restore();
      });
      
      ctx.restore();
    }

    // Smooth animation loop with RAF timing
    let lastTime = 0;
    function modernFrame(currentTime) {
      const deltaTime = currentTime - lastTime;
      lastTime = currentTime;
      
      // Adaptive quality based on performance
      if (deltaTime > 33) { // If frame rate drops below 30fps
        ctx.imageSmoothingEnabled = false;
      } else {
        ctx.imageSmoothingEnabled = true;
      }
      
      drawModernGrid(currentTime);
      drawModernLambda(currentTime);
      drawModernCorners(currentTime);
      
      requestAnimationFrame(modernFrame);
    }
    requestAnimationFrame(modernFrame);
  }
  
  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initLambdaGrid);
  } else {
    initLambdaGrid();
  }
})();

// Initialize the experience when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  console.log('DOM loaded, initializing intro experience...');

  // Start the luxury intro experience
  new LuxuryIntroExperience();
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    // Pause animations when page is hidden
    document.body.style.animationPlayState = 'paused';
  } else {
    // Resume animations when page is visible
    document.body.style.animationPlayState = 'running';
  }
});

// Performance optimization for slower devices
const optimizeForPerformance = () => {
  const isLowPerformance = navigator.hardwareConcurrency < 4 ||
    (navigator.deviceMemory && navigator.deviceMemory < 4) ||
    navigator.userAgent.includes('Mobile');

  if (isLowPerformance) {
    console.log('Optimizing for low performance device');
    // Reduce particle count and effects
    document.documentElement.style.setProperty('--transition-luxury', '0.4s ease');
    document.documentElement.style.setProperty('--transition-smooth', '0.3s ease');

    // Disable texture overlay
    const style = document.createElement('style');
    style.textContent = `
      body::before { display: none; }
      .glow-orb { display: none; }
      .ambient-shapes { display: none; }
    `;
    document.head.appendChild(style);
  }
};

// Apply performance optimizations
optimizeForPerformance();

// Export for external use and debugging
window.LUKHAS_AI_INTRO = {
  skip: () => window.introExperience?.skipIntro(),
  enter: () => window.introExperience?.enterExperience(),
  getCurrentPhase: () => window.introExperience?.currentPhase,
  goToPhase: (phase) => window.introExperience?.transitionToPhase(phase)
};