---
status: wip
type: documentation
---
# Migration Checklist: Unified Consciousness Visualizer

## Summary

The new Unified Consciousness Visualizer consolidates the text-to-shape and voice-reactive-morph systems into a single, comprehensive visualization engine with enhanced LUKHAS consciousness integration.

## Files to Remove After Migration

### Text-to-Shape System (External)
Located in: `/Users/agi_dev/Documents/ text‑to‑shape /`

- [ ] `ai-shape-controller.js` - Replaced by unified engine's text morphing
- [ ] `morphing-engine.js` - Integrated into unified particle system
- [ ] `morphing-system.patch.js` - No longer needed
- [ ] `text-shape-morph-target.js` - Functionality in unified engine
- [ ] `shader-modifications.js` - WebGL shaders now in unified system
- [ ] `README_integration.md` - Superseded by unified documentation

### Voice-Reactive Morphing System (External)
Located in: `/Users/agi_dev/Downloads/voice_reactive_morphing/`

- [ ] `ai-voice-integration.js` - Voice analysis now in unified engine
- [ ] `api-keys.js` - API configuration handled differently
- [ ] `build.js` - Build process no longer needed
- [ ] `config.js` - Configuration in unified system
- [ ] `content.script.js` - Browser extension features removed
- [ ] `keychain-integration.js` - Security handled by main system
- [ ] `main.html` - Replaced by unified index.html
- [ ] `index.html` - Replaced by unified interface
- [ ] `test-boundaries.html` - Test integrated into main demo
- [ ] `test-shape-frames.html` - Test integrated into main demo
- [ ] `shader-modifications.js` - Duplicate, shaders in unified system
- [ ] All documentation files in this folder

### Legacy LUKHAS Visualization Files

#### Can be removed if not used elsewhere:
- [ ] `/Users/agi_dev/LOCAL-REPOS/Lukhas/governance/identity/web_interface/threejs_visualizer.js`
  - **Note**: Check if other identity systems depend on this

#### Should be updated to use unified system:
- [ ] `/Users/agi_dev/LOCAL-REPOS/Lukhas/matada_agi/frontend/components/dream/ConsciousnessVisualizer.tsx`
  - **Action**: Update to import and use UnifiedConsciousnessVisualizer

- [ ] `/Users/agi_dev/LOCAL-REPOS/Lukhas/matada_agi/frontend/components/sections/TrinityCanvas.tsx`
  - **Action**: Can optionally migrate to use unified system for consistency

### Workspace Configuration
- [ ] Update `/Users/agi_dev/LOCAL-REPOS/Lukhas/Lukhas.code-workspace`
  - Remove references to external folders:
    - `../../Downloads/voice_reactive_morphing`
    - `../../Documents/ text‑to‑shape `

## Migration Steps

### 1. Test Unified System
```bash
# Navigate to unified visualization
cd /Users/agi_dev/LOCAL-REPOS/Lukhas/visualization/unified

# Start local server
python -m http.server 8000

# Open http://localhost:8000 in browser
# Test all features:
# - Text morphing
# - Voice reactivity (requires HTTPS or localhost)
# - Shape transitions
# - Consciousness state changes
```

### 2. Update Existing Integrations

#### For React/Next.js Components:
```typescript
// Old import
import ConsciousnessVisualizer from './ConsciousnessVisualizer';

// New import
import { UnifiedConsciousnessVisualizer } from '@/visualization/unified/unified_consciousness_visualizer';

// Usage
useEffect(() => {
  const visualizer = new UnifiedConsciousnessVisualizer({
    containerId: 'viz-container',
    particleCount: 15000,
    enableVoice: true
  });

  return () => visualizer.destroy();
}, []);
```

#### For Python Integration:
```python
# Import the bridge
from visualization.unified.consciousness_integration import (
    ConsciousnessVisualizationBridge,
    VisualizationMode
)

# Use in existing consciousness systems
bridge = ConsciousnessVisualizationBridge()
params = bridge.get_visualization_params()
```

### 3. Update Documentation References

Files that may reference old visualization systems:
- [ ] Main README.md
- [ ] API documentation
- [ ] Integration guides
- [ ] Development setup guides

### 4. Backup Before Removal

```bash
# Create backup of old systems
mkdir -p /Users/agi_dev/lukhas-archive/visualization-legacy

# Backup text-to-shape
cp -r "/Users/agi_dev/Documents/ text‑to‑shape /" \
      /Users/agi_dev/lukhas-archive/visualization-legacy/text-to-shape

# Backup voice-reactive
cp -r /Users/agi_dev/Downloads/voice_reactive_morphing \
      /Users/agi_dev/lukhas-archive/visualization-legacy/

# Backup any LUKHAS files
cp /Users/agi_dev/LOCAL-REPOS/Lukhas/governance/identity/web_interface/threejs_visualizer.js \
   /Users/agi_dev/lukhas-archive/visualization-legacy/
```

### 5. Remove Obsolete Files

```bash
# Remove external folders (after confirming backup)
rm -rf "/Users/agi_dev/Documents/ text‑to‑shape /"
rm -rf /Users/agi_dev/Downloads/voice_reactive_morphing

# Remove or update LUKHAS legacy files as needed
```

### 6. Update Workspace

Edit `/Users/agi_dev/LOCAL-REPOS/Lukhas/Lukhas.code-workspace`:
```json
{
    "folders": [
        {
            "path": "."
        }
        // Remove external folder references
    ]
}
```

## Verification Checklist

After migration, verify:

- [ ] Unified visualizer loads without errors
- [ ] Text morphing works correctly
- [ ] Voice input responds (if HTTPS/localhost)
- [ ] All shapes render properly
- [ ] Consciousness state updates reflect visually
- [ ] Performance meets targets (60fps with 20k particles)
- [ ] No console errors or warnings
- [ ] Documentation is updated
- [ ] All integrations work correctly

## Benefits of Migration

1. **Unified Codebase**: Single source of truth for all visualization
2. **Better Performance**: Optimized particle system and rendering
3. **Easier Maintenance**: One system to update and debug
4. **Enhanced Features**: Consciousness integration, more shapes, better controls
5. **Cleaner Architecture**: Modular design with clear separation of concerns
6. **Reduced Dependencies**: Fewer external files and configurations
7. **Consistent API**: Single API for all visualization needs

## Rollback Plan

If issues arise:

1. Restore from backup created in step 4
2. Re-add workspace folder references
3. Document specific issues for resolution
4. Consider gradual migration if needed

## Support

For migration assistance:
- Review unified system documentation: `/visualization/unified/README.md`
- Test with demo: `/visualization/unified/index.html`
- Check console for specific error messages
- Ensure all prerequisites are met (Three.js, WebGL support)
