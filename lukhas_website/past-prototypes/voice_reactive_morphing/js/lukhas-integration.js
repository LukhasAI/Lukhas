/**
 * LUKHAS Integration Module for PR0T3US
 * Handles communication between the LUKHAS website and PR0T3US visualizer
 */

(function() {
  'use strict';

  // Check if we're running in an iframe
  const isEmbedded = window.parent !== window;

  // Get URL parameters
  const urlParams = new URLSearchParams(window.location.search);
  const embeddedMode = urlParams.get('embedded') === 'true';
  const initialMicState = urlParams.get('mic') === 'true';
  const initialAudioState = urlParams.get('audio') !== 'false'; // Default to true

  // Initialize state
  const state = {
    micEnabled: initialMicState,
    audioEnabled: initialAudioState,
    isReady: false,
    apiConfig: {},
    visualConfig: {}
  };

  // Load saved configuration from localStorage
  function loadConfiguration() {
    try {
      const savedApiConfig = localStorage.getItem('proteus_api_config');
      const savedVisualConfig = localStorage.getItem('proteus_visual_config');

      if (savedApiConfig) {
        state.apiConfig = JSON.parse(savedApiConfig);
      }
      if (savedVisualConfig) {
        state.visualConfig = JSON.parse(savedVisualConfig);
        applyVisualConfiguration(state.visualConfig);
      }
    } catch (error) {
      console.error('Error loading configuration:', error);
    }
  }

  // Apply visual configuration to the system
  function applyVisualConfiguration(config) {
    if (window.morphingSystem) {
      // Apply particle settings
      if (config.particleCount !== undefined) {
        window.morphingSystem.setParticleCount(config.particleCount);
      }
      if (config.morphSpeed !== undefined) {
        window.morphingSystem.setMorphSpeed(config.morphSpeed);
      }
      if (config.voiceIntensity !== undefined) {
        window.morphingSystem.setVoiceIntensity(config.voiceIntensity);
      }

      // Update UI sliders if they exist
      updateUIFromConfig(config);
    }
  }

  // Update UI elements from configuration
  function updateUIFromConfig(config) {
    const elements = {
      particleCount: document.getElementById('particleCount'),
      particleCountValue: document.getElementById('particleCountValue'),
      morphSpeed: document.getElementById('morphSpeed'),
      morphSpeedValue: document.getElementById('morphSpeedValue'),
      voiceIntensity: document.getElementById('voiceIntensity'),
      voiceIntensityValue: document.getElementById('voiceIntensityValue'),
      boundaryForce: document.getElementById('boundaryForce'),
      boundaryForceValue: document.getElementById('boundaryForceValue'),
      attractionStrength: document.getElementById('attractionStrength'),
      attractionStrengthValue: document.getElementById('attractionStrengthValue'),
      particleSize: document.getElementById('particleSize'),
      particleSizeValue: document.getElementById('particleSizeValue')
    };

    if (config.particleCount !== undefined && elements.particleCount) {
      elements.particleCount.value = config.particleCount;
      if (elements.particleCountValue) {
        elements.particleCountValue.textContent = config.particleCount;
      }
    }
    if (config.morphSpeed !== undefined && elements.morphSpeed) {
      elements.morphSpeed.value = config.morphSpeed;
      if (elements.morphSpeedValue) {
        elements.morphSpeedValue.textContent = config.morphSpeed.toFixed(1);
      }
    }
    if (config.voiceIntensity !== undefined && elements.voiceIntensity) {
      elements.voiceIntensity.value = config.voiceIntensity;
      if (elements.voiceIntensityValue) {
        elements.voiceIntensityValue.textContent = config.voiceIntensity.toFixed(1);
      }
    }
    if (config.boundaryForce !== undefined && elements.boundaryForce) {
      elements.boundaryForce.value = config.boundaryForce;
      if (elements.boundaryForceValue) {
        elements.boundaryForceValue.textContent = config.boundaryForce.toFixed(2);
      }
    }
    if (config.attractionStrength !== undefined && elements.attractionStrength) {
      elements.attractionStrength.value = config.attractionStrength;
      if (elements.attractionStrengthValue) {
        elements.attractionStrengthValue.textContent = config.attractionStrength.toFixed(1);
      }
    }
    if (config.particleSize !== undefined && elements.particleSize) {
      elements.particleSize.value = config.particleSize;
      if (elements.particleSizeValue) {
        elements.particleSizeValue.textContent = config.particleSize.toFixed(1);
      }
    }
  }

  // Handle messages from parent window
  function handleMessage(event) {
    // Security: Only accept messages from trusted origins
    const trustedOrigins = [
      'http://localhost:3000',
      'http://localhost:3001',
      'https://lukhas.ai',
      'https://www.lukhas.ai'
    ];

    const isLocalhost = event.origin.includes('localhost');
    const isLukhas = event.origin.includes('lukhas.ai');

    if (!isLocalhost && !isLukhas) {
      return;
    }

    const { type, ...data } = event.data;

    switch (type) {
      case 'updateSettings':
        handleUpdateSettings(data);
        break;

      case 'updateConfiguration':
        handleUpdateConfiguration(data);
        break;

      case 'proteusCommand':
        handleCommand(data.command, data.data);
        break;

      case 'requestStatus':
        sendStatus();
        break;
    }
  }

  // Handle settings update
  function handleUpdateSettings(settings) {
    if (settings.micEnabled !== undefined) {
      state.micEnabled = settings.micEnabled;
      toggleMicrophone(settings.micEnabled);
    }
    if (settings.audioEnabled !== undefined) {
      state.audioEnabled = settings.audioEnabled;
      toggleAudio(settings.audioEnabled);
    }
  }

  // Handle configuration update
  function handleUpdateConfiguration(data) {
    if (data.apiConfig) {
      state.apiConfig = data.apiConfig;
      localStorage.setItem('proteus_api_config', JSON.stringify(data.apiConfig));
      applyApiConfiguration(data.apiConfig);
    }
    if (data.visualConfig) {
      state.visualConfig = data.visualConfig;
      localStorage.setItem('proteus_visual_config', JSON.stringify(data.visualConfig));
      applyVisualConfiguration(data.visualConfig);
    }
  }

  // Apply API configuration
  function applyApiConfiguration(config) {
    // Update API key inputs if they exist
    const openaiInput = document.getElementById('openaiKey');
    const anthropicInput = document.getElementById('anthropicKey');
    const localEndpointInput = document.getElementById('localEndpoint');

    if (openaiInput && config.openaiKey) {
      openaiInput.value = config.openaiKey;
    }
    if (anthropicInput && config.anthropicKey) {
      anthropicInput.value = config.anthropicKey;
    }
    if (localEndpointInput && config.localEndpoint) {
      localEndpointInput.value = config.localEndpoint;
    }
  }

  // Handle commands from parent
  function handleCommand(command, data) {
    switch (command) {
      case 'setShape':
        if (window.morphingSystem && data.shape) {
          window.morphingSystem.setShape(data.shape);
        }
        break;

      case 'setColor':
        if (window.morphingSystem && data.color) {
          window.morphingSystem.setColor(data.color);
        }
        break;

      case 'setParticleCount':
        if (window.morphingSystem && data.count) {
          window.morphingSystem.setParticleCount(data.count);
        }
        break;

      case 'reset':
        if (window.morphingSystem) {
          window.morphingSystem.reset();
        }
        break;

      case 'toggleMic':
        toggleMicrophone(!state.micEnabled);
        break;

      case 'toggleAudio':
        toggleAudio(!state.audioEnabled);
        break;
    }
  }

  // Toggle microphone
  function toggleMicrophone(enable) {
    state.micEnabled = enable;
    const micButton = document.getElementById('toggleMicrophone');
    if (micButton) {
      micButton.textContent = enable ? 'Disable Mic' : 'Enable Mic';
      micButton.classList.toggle('active', enable);
    }

    // Trigger actual microphone toggle in the morphing system
    if (window.morphingSystem) {
      window.morphingSystem.toggleMicrophone(enable);
    }
  }

  // Toggle audio
  function toggleAudio(enable) {
    state.audioEnabled = enable;
    // Implement audio toggle logic
    if (window.morphingSystem) {
      window.morphingSystem.toggleAudio(enable);
    }
  }

  // Send status to parent window
  function sendStatus() {
    if (isEmbedded && window.parent) {
      window.parent.postMessage({
        type: 'proteusStatus',
        ready: state.isReady,
        micEnabled: state.micEnabled,
        audioEnabled: state.audioEnabled
      }, '*');
    }
  }

  // Send ready signal
  function sendReady() {
    state.isReady = true;
    if (isEmbedded && window.parent) {
      window.parent.postMessage({
        type: 'proteusReady'
      }, '*');
    }
  }

  // Hide UI elements in embedded mode
  function configureEmbeddedMode() {
    if (embeddedMode) {
      // Hide the top bar and chat panel in embedded mode
      const topBar = document.querySelector('.lucas-topbar');
      const chatPanel = document.getElementById('lucasChatPanel');

      if (topBar) {
        topBar.style.display = 'none';
      }
      if (chatPanel) {
        chatPanel.style.display = 'none';
      }

      // Adjust canvas to full size
      const canvas = document.getElementById('mainCanvas');
      if (canvas) {
        canvas.style.top = '0';
        canvas.style.height = '100vh';
      }
    }
  }

  // Initialize on DOM ready
  function initialize() {
    loadConfiguration();
    configureEmbeddedMode();

    // Set up message listener
    if (isEmbedded) {
      window.addEventListener('message', handleMessage);
    }

    // Apply initial states
    if (state.micEnabled) {
      toggleMicrophone(true);
    }
    if (!state.audioEnabled) {
      toggleAudio(false);
    }

    // Send ready signal after a short delay to ensure everything is loaded
    setTimeout(sendReady, 1000);
  }

  // Wait for DOM to be ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
  } else {
    initialize();
  }

  // Expose integration API globally
  window.lukhasIntegration = {
    state,
    sendStatus,
    applyVisualConfiguration,
    applyApiConfiguration,
    toggleMicrophone,
    toggleAudio
  };
})();
