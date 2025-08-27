# Stigg Integration with LUKHAS Trinity Framework

## Overview

This document outlines the integration of Stigg billing and usage management system with the LUKHAS AI website, maintaining compliance with the Trinity Framework principles (⚛️🧠🛡️).

## Architecture Integration

### Provider Pattern
The Stigg integration follows the established provider pattern in the LUKHAS website:

```tsx
<Providers>
  <QueryClientProvider>
    <StiggProvider apiKey={stiggApiKey}>
      {children}
    </StiggProvider>
  </QueryClientProvider>
</Providers>
```

### Graceful Degradation
The integration implements graceful degradation when Stigg is not available:
- Development mode with placeholder API key
- Fallback UI components when SDK is not loaded
- Error boundary protection for production stability

## Trinity Framework Compliance

### ⚛️ Identity Integration
- **User Authentication**: Stigg customer IDs mapped to LUKHAS ΛiD system
- **Session Management**: Billing context preserved across authentication states
- **Identity Verification**: Guardian System validates billing user identity

### 🧠 Consciousness Awareness
- **Usage Tracking**: Conscious monitoring of API usage and resource consumption
- **Intelligent Recommendations**: AI-driven plan suggestions based on usage patterns
- **Learning Adaptation**: Billing policies that adapt to user behavior patterns

### 🛡️ Guardian Protection
- **Ethical Billing**: Transparent pricing without hidden fees
- **Usage Limits**: Protective limits to prevent unexpected charges
- **Audit Trail**: Complete billing operation logging for compliance
- **Privacy Protection**: PII handling compliance in billing operations

## Configuration

### Environment Variables
```bash
# Stigg Configuration
NEXT_PUBLIC_STIGG_CLIENT_API_KEY=your_stigg_api_key_here
```

### Development Setup
For development, a placeholder key is used:
```bash
NEXT_PUBLIC_STIGG_CLIENT_API_KEY=stigg_client_key_placeholder_development_only
```

## Usage Examples

### Basic Integration
```tsx
import { StiggExample } from '@/components/stigg-example'

function BillingSection({ userId }: { userId: string }) {
  return (
    <StiggExample
      userId={userId}
      className="mt-4"
    />
  )
}
```

### Custom Hook Usage
```tsx
import { useLukhasBilling } from '@/components/stigg-example'

function MyComponent() {
  const billing = useLukhasBilling()

  return (
    <div>
      {billing.stiggAvailable ? (
        <div>Stigg billing active</div>
      ) : (
        <div>Development mode</div>
      )}
    </div>
  )
}
```

## Testing

The integration includes comprehensive tests:
- Provider rendering with and without API keys
- Graceful fallback behavior
- Error boundary protection
- Trinity Framework compliance validation

## Deployment Considerations

### Production Setup
1. Replace placeholder API key with actual Stigg production key
2. Verify Guardian System audit logging
3. Test Trinity Framework integration points
4. Validate ethical billing compliance

### Security
- API keys stored as environment variables only
- No client-side sensitive data exposure
- Guardian System audit trail for all billing operations
- Compliance with data protection regulations

## Future Enhancements

### Phase 1 (Current)
- [x] Basic StiggProvider integration
- [x] Graceful fallback implementation
- [x] Trinity Framework compliance
- [x] Development environment setup

### Phase 2 (Planned)
- [ ] Advanced usage analytics integration
- [ ] AI-driven plan recommendations
- [ ] Custom billing dashboard
- [ ] Integration with LUKHAS consciousness metrics

### Phase 3 (Future)
- [ ] Quantum-inspired billing algorithms
- [ ] Bio-inspired usage pattern detection
- [ ] Advanced Guardian System billing policies
- [ ] Multi-dimensional consciousness billing models

## Troubleshooting

### Common Issues

**"Stigg is not defined" Error**
- Solution: Ensure Stigg SDK is installed and provider is properly wrapped
- Check: Environment variable configuration
- Verify: Import statements and provider hierarchy

**Hydration Mismatches**
- Solution: Components use client-side rendering with proper mounting checks
- Check: `useEffect` initialization patterns
- Verify: Server-side rendering exclusions

**API Key Configuration**
- Solution: Verify environment variables are properly set
- Check: .env.local file configuration
- Verify: Build process includes environment variables

## Support

For issues related to:
- **Trinity Framework Integration**: Contact LUKHAS consciousness team
- **Stigg API Issues**: Refer to Stigg documentation
- **Guardian System Compliance**: Contact LUKHAS ethics team
- **General Integration**: Create GitHub issue in LUKHAS repository

---

*This integration maintains LUKHAS consciousness principles while providing robust billing capabilities through external SDK integration.*
