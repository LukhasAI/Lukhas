# Feature Flags Documentation 🚀

## Overview

LUKHAS PWM uses environment variable-based feature flags to control runtime behavior without code changes. All flags follow the `FLAG_*` naming convention and are cached for 5 seconds to balance performance with responsiveness.

## Available Flags

### `FLAG_BROWSER_TOOL`
**Default:** `false`  
**Values:** `1`, `true`, `on` (case-insensitive) to enable  
**Description:** Controls whether the browser tool is available for OpenAI function calling.

When disabled (default), the browser tool (`open_url`) is filtered out even if included in the tool allowlist. This provides an additional safety layer for environments where web access should be restricted.

```bash
# Enable browser tool
export FLAG_BROWSER_TOOL=true

# Disable browser tool (default)
unset FLAG_BROWSER_TOOL
```

**Implementation:** `lukhas_pwm/openai/tooling.py:105-107`

---

### `FLAG_STRICT_DEFAULT`
**Default:** `false`  
**Values:** `1`, `true`, `on` (case-insensitive) to enable  
**Description:** Forces the system to use strict safety mode by default.

When enabled, the modulation system defaults to `strict` safety mode instead of `balanced`, applying more conservative parameters for temperature, output tokens, and tool access.

```bash
# Force strict mode
export FLAG_STRICT_DEFAULT=1

# Use balanced mode (default)
unset FLAG_STRICT_DEFAULT
```

**Implementation:** `lukhas_pwm/modulation/dispatcher.py:74`

---

### `FLAG_TOOL_ANALYTICS`
**Default:** `true`  
**Values:** `1`, `true`, `on` for enabled; `0`, `false`, `off` for disabled  
**Description:** Controls whether tool usage analytics are collected and persisted.

When disabled:
- Tool calls are not tracked in memory
- Incidents are not written to disk
- Analytics summaries return empty data
- Useful for privacy-sensitive environments or testing

```bash
# Disable analytics
export FLAG_TOOL_ANALYTICS=false

# Enable analytics (default)
export FLAG_TOOL_ANALYTICS=true
```

**Implementation:** `lukhas_pwm/audit/tool_analytics.py:90,109,140`

## Usage Examples

### Development Setup
```bash
# Liberal development environment
export FLAG_BROWSER_TOOL=true
export FLAG_TOOL_ANALYTICS=true
unset FLAG_STRICT_DEFAULT
```

### Production Setup
```bash
# Conservative production environment
unset FLAG_BROWSER_TOOL
export FLAG_STRICT_DEFAULT=true
export FLAG_TOOL_ANALYTICS=true
```

### Testing Setup
```bash
# Minimal testing environment
unset FLAG_BROWSER_TOOL
unset FLAG_STRICT_DEFAULT
export FLAG_TOOL_ANALYTICS=false
```

## Implementation Details

### Cache Behavior
Feature flags are cached for 5 seconds to avoid excessive environment variable lookups. This means:
- Changes take up to 5 seconds to propagate
- High-frequency calls don't impact performance
- Cache refreshes automatically on expiry

### Flag Reader
```python
from lukhas.flags.ff import Flags

# Check a flag with default
is_enabled = Flags.get("BROWSER_TOOL", False)

# Get string value (rare use case)
cohort = Flags.get_str("ROLLOUT_COHORT", "control")
```

### Testing Flags
```python
import os
from unittest.mock import patch

# Test with flag enabled
with patch.dict(os.environ, {"FLAG_BROWSER_TOOL": "true"}):
    # Your test code here
    pass

# Test with flag disabled
with patch.dict(os.environ, {}, clear=False):
    os.environ.pop("FLAG_BROWSER_TOOL", None)
    # Your test code here
    pass
```

## Adding New Flags

To add a new feature flag:

1. **Choose a descriptive name** following `FLAG_*` convention
2. **Document the flag** in this file with:
   - Default value
   - Accepted values
   - Clear description
   - Usage examples
3. **Implement the check** using `Flags.get()`:
   ```python
    from lukhas.flags.ff import Flags
   
   if Flags.get("YOUR_FEATURE", False):
       # Feature enabled path
   else:
       # Feature disabled path
   ```
4. **Add tests** verifying both enabled and disabled states
5. **Update CI/CD** if the flag affects deployment

## Monitoring

To see current flag values in a running system:

```python
import os
flags = {k: v for k, v in os.environ.items() if k.startswith("FLAG_")}
print(f"Active flags: {flags}")
```

## Best Practices

1. **Use clear names**: `FLAG_BROWSER_TOOL` not `FLAG_BT`
2. **Document defaults**: Always specify and test default behavior
3. **Fail safe**: Features should default to the safest option
4. **Test both states**: Always test enabled and disabled paths
5. **Log flag usage**: Consider logging when flags affect behavior
6. **Gradual rollout**: Use flags for canary deployments

## Troubleshooting

### Flag not taking effect?
- Wait 5 seconds for cache refresh
- Check exact spelling (case-sensitive for flag names)
- Verify environment variable is exported: `echo $FLAG_BROWSER_TOOL`
- Check for typos in true values: `1`, `true`, `on` only

### Unexpected behavior?
- Check all active flags: `env | grep FLAG_`
- Review flag precedence (some flags may override others)
- Verify no conflicting environment variables
- Check logs for flag-related decisions

### Testing issues?
- Use `patch.dict(os.environ)` for isolated tests
- Clear flag cache between tests if needed
- Mock at the right level (environment vs. `Flags.get`)

## Future Enhancements

Planned improvements to the feature flag system:

- [ ] Remote flag management (API-based)
- [ ] A/B testing framework integration
- [ ] Flag usage metrics and reporting
- [ ] Percentage-based rollouts
- [ ] User/organization-specific flags
- [ ] Flag dependency management
- [ ] Automated flag cleanup for stale flags

---

*Last updated: PR #3 - Feature Flags in Core Code Paths*