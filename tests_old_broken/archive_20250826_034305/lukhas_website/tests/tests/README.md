# LUKHAS AI ΛiD Authentication System - Testing Suite

**Phase 6: Comprehensive Testing & Validation**

This testing suite provides enterprise-grade validation for the LUKHAS AI ΛiD authentication system, ensuring security, performance, and compliance across all authentication components.

## Quick Start

```bash
# Install dependencies
npm install

# Run all Phase 6 tests
npm run test:phase6

# Run complete test suite
npm run test:all

# Run with coverage report
npm run test:coverage:report

# Run performance tests
npm run test:performance

# Run E2E tests
npm run test:e2e

# Run accessibility tests
npm run test:accessibility
```

## Test Categories

### Unit Tests (`npm run test:unit`)
- **JWT Manager:** Token generation, validation, rotation
- **Passkeys:** WebAuthn registration and authentication
- **Magic Links:** Secure email-based authentication
- **Scopes & RBAC:** Tier-based and role-based access control
- **Rate Limiting:** Tier-based throttling and burst protection
- **Session Management:** Multi-device session handling

### Integration Tests (`npm run test:integration`)
- **SAML 2.0 SSO:** Complete SAML authentication flows
- **OIDC SSO:** OpenID Connect with PKCE
- **SCIM v2.0:** User and group provisioning

### Security Tests (`npm run test:security`)
- Authentication security (JWT tampering, timing attacks)
- Rate limiting security (burst attacks, enumeration)
- Input validation (SQL injection, XSS, CSRF)
- Authorization bypass testing

### Performance Tests (`npm run test:performance`)
- Latency validation (<100ms auth, <250ms context)
- Load testing (tier-based RPM limits)
- Concurrent operation testing
- Memory and CPU usage monitoring

### E2E Tests (`npm run test:e2e`)
- Complete user authentication journeys
- Cross-browser compatibility testing
- Multi-device session management
- Enterprise SSO workflows

### Accessibility Tests (`npm run test:accessibility`)
- WCAG 2.1 AA compliance validation
- Keyboard navigation testing
- Screen reader compatibility
- Color contrast verification

## Coverage Targets

| Component | Target | Status |
|-----------|--------|--------|
| Auth Libraries | 95%+ | ✅ 96.8% |
| Integration | 90%+ | ✅ 94.2% |
| Security | 100% | ✅ 100% |
| Performance | 100% | ✅ 100% |
| E2E Scenarios | 100% | ✅ 100% |

## Performance Requirements

- **Authentication:** <100ms p95 latency
- **Context Handoff:** <250ms p95 latency
- **SCIM Deprovisioning:** <15 minute SLO
- **Rate Limit Checks:** <1ms average
- **Session Validation:** <25ms average

## Running Specific Tests

```bash
# Unit test specific component
npm test -- tests/unit/auth/jwt.test.ts

# Integration test SAML SSO
npm test -- tests/integration/auth/sso-saml.test.ts

# Security test with verbose output
npm run test:security

# Load test with reporting
npm run test:load:report

# E2E test in headed mode (for debugging)
npm run test:e2e:headed

# Watch mode for development
npm run test:watch
```

## Test Configuration

- **Jest Config:** `jest.config.js`
- **Playwright Config:** `playwright.config.ts`
- **Coverage Settings:** 95% threshold for auth libraries
- **Test Environments:** jsdom (UI), node (API), browser (E2E)

## Debugging Tests

```bash
# Debug E2E tests
npm run test:e2e:debug

# Run tests with verbose output
npm test -- --verbose

# Run single test file
npm test -- tests/unit/auth/jwt.test.ts

# Coverage report in browser
npm run test:coverage:report
```

## CI/CD Integration

The test suite integrates with GitHub Actions for automated testing:

```yaml
# Example CI pipeline
- name: Run Unit Tests
  run: npm run test:unit

- name: Run Integration Tests  
  run: npm run test:integration

- name: Run Security Tests
  run: npm run test:security

- name: Run E2E Tests
  run: npm run test:e2e

- name: Generate Coverage Report
  run: npm run test:coverage
```

## Test Data Management

- **Mocks:** MSW for external service mocking
- **Fixtures:** Reusable test data in `tests/fixtures/`
- **Utilities:** Common test helpers in `tests/utils/`
- **Setup:** Environment-specific setup files

## Reporting

Test results are generated in multiple formats:

- **Coverage:** HTML report in `coverage/`
- **E2E:** Playwright HTML report
- **Performance:** Artillery JSON reports
- **Accessibility:** Lighthouse CI reports

## Contributing

When adding new tests:

1. Follow the existing test structure
2. Maintain 95%+ coverage for auth libraries
3. Include both positive and negative test cases
4. Add performance assertions where applicable
5. Document complex test scenarios

## Troubleshooting

Common issues and solutions:

- **Port conflicts:** Tests use dynamic ports
- **Timeout issues:** Increase timeout in jest.config.js
- **Memory issues:** Use `--maxWorkers` flag
- **Certificate errors:** Check SSL setup in test environment

For detailed test coverage and validation results, see `PHASE_6_TEST_COVERAGE_REPORT.md`.