---
module: integrations
title: PR0T3US Integration with LUKHAS Website
---

# PR0T3US Integration with LUKHAS Website

## Overview
PR0T3US is a sophisticated voice-reactive 3D morphing system that visualizes consciousness through WebGL particle systems. It has been seamlessly integrated into the LUKHAS website to provide an immersive experience for users.

## Architecture

### Components
1. **PR0T3US Visualizer** (`/voice_reactive_morphing/`)
   - Standalone WebGL application
   - Voice-reactive particle systems
   - AI integration capabilities
   - Runs on port 8080

2. **LUKHAS Website** (`/lukhas_website/`)
   - Next.js application
   - Premium UI with dark theme
   - Hosts the Experience page
   - Runs on port 3000

3. **Integration Layer**
   - iframe embedding with postMessage communication
   - Configuration synchronization
   - Cross-origin security handling

## Quick Start

### Method 1: Automated Startup
```bash
cd lukhas_website/scripts
./start-with-proteus.sh
```
This will start both services and open:
- Website: http://localhost:3000
- Experience: http://localhost:3000/experience
- PR0T3US Direct: http://localhost:8080

### Method 2: Manual Startup

#### Start PR0T3US Server
```bash
cd voice_reactive_morphing
npm install
npm start
# Server runs on http://localhost:8080
```

#### Start LUKHAS Website
```bash
cd lukhas_website
npm install
npm run dev
# Website runs on http://localhost:3000
```

## Features

### Experience Page (`/experience`)
- **Voice Interaction**: Enable microphone for voice-reactive shapes
- **Real-time Visualization**: Watch particles respond to voice and emotions
- **Configuration Panel**: Set up AI provider API keys
- **Onboarding Tutorial**: First-time user guidance

### Voice Commands
- "Show me consciousness" - Neural pattern visualization
- "Transform to cube" - Geometric shape morphing
- "Increase energy" - Amplify particle dynamics

### Visualization Controls
- **Mouse Controls**:
  - Left-click + drag: Rotate view
  - Right-click + drag: Pan camera
  - Scroll: Zoom in/out
  - Double-click: Reset view

### Configuration Options
- **API Providers**:
  - OpenAI GPT-4
  - Anthropic Claude
  - Google Gemini
  - Local models (Ollama)

- **Visual Settings**:
  - Particle count (100-5000)
  - Morph speed
  - Voice intensity
  - Color schemes (Consciousness, Identity, Guardian)

## Technical Details

### Communication Protocol
The iframe integration uses postMessage for secure cross-origin communication:

```javascript
// Parent to PR0T3US
window.postMessage({
  type: 'updateSettings',
  micEnabled: true,
  audioEnabled: true
}, '*')

// PR0T3US to Parent
window.parent.postMessage({
  type: 'proteusReady'
}, '*')
```

### Security
- CORS configured for LUKHAS domains
- X-Frame-Options set to SAMEORIGIN
- Content Security Policy for iframe embedding
- API keys stored in localStorage (client-side only)

### File Structure
```
lukhas_website/
├── app/
│   ├── experience/
│   │   └── page.tsx          # Experience page
│   └── page.tsx              # Updated homepage
├── components/
│   ├── proteus-visualizer.tsx   # Iframe wrapper
│   ├── proteus-config.tsx       # Configuration panel
│   └── proteus-onboarding.tsx   # Tutorial overlay
└── scripts/
    └── start-with-proteus.sh    # Startup script

voice_reactive_morphing/
├── index.html                   # PR0T3US main file
├── server.js                    # Express server
├── package.json                 # Dependencies
└── js/
    └── lukhas-integration.js    # Integration module
```

## Development

### Adding New Voice Commands
Edit `/voice_reactive_morphing/js/morphing-system.js` to add voice command handlers.

### Customizing Visual Themes
Modify color schemes in `/voice_reactive_morphing/shader-modifications.js`.

### Updating Configuration Options
1. Add UI controls in `/lukhas_website/components/proteus-config.tsx`
2. Handle messages in `/voice_reactive_morphing/js/lukhas-integration.js`

## Deployment

### Production Setup
1. Build the Next.js app:
   ```bash
   cd lukhas_website
   npm run build
   ```

2. Configure environment variables:
   ```env
   NEXT_PUBLIC_PROTEUS_URL=https://proteus.lukhas.ai
   ```

3. Deploy PR0T3US to a static hosting service or CDN

4. Update CORS settings in `server.js` for production domains

## Troubleshooting

### PR0T3US not loading
- Check if port 8080 is available
- Verify Next.js rewrites in `next.config.js`
- Check browser console for CORS errors

### Microphone not working
- Ensure HTTPS in production (required for getUserMedia)
- Check browser permissions
- Verify microphone is not in use by another application

### Performance issues
- Reduce particle count in settings
- Disable unnecessary visual effects
- Check GPU acceleration in browser settings

## Future Enhancements
- WebRTC for real-time collaboration
- Mobile app integration
- VR/AR support
- Advanced AI consciousness models
- Multi-user shared experiences

## Support
For issues or questions, please refer to the main LUKHAS documentation or contact the development team.
