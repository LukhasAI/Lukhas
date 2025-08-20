/**
 * LUKHAS AI ΛiD Authentication System - Global Test Teardown
 * Phase 6: Comprehensive Testing & Validation
 * 
 * Global teardown for all Jest test suites
 */

async function globalTeardown() {
  console.log('🧹 Cleaning up LUKHAS AI ΛiD Authentication Test Environment...');

  // Clean up test files
  const fs = require('fs').promises;
  const path = require('path');

  try {
    // Clean up temporary test files (keep test results for CI)
    const tempDirs = [
      'temp',
      '.tmp',
    ];

    for (const dir of tempDirs) {
      const dirPath = path.join(process.cwd(), dir);
      try {
        await fs.rmdir(dirPath, { recursive: true });
      } catch (error) {
        // Directory might not exist, ignore
      }
    }

    // Generate final test report summary
    await generateTestSummary();

    console.log('✅ Test environment cleanup complete');
  } catch (error) {
    console.error('❌ Error during test cleanup:', error);
  }
}

async function generateTestSummary() {
  const fs = require('fs').promises;
  const path = require('path');

  try {
    const summaryPath = path.join(process.cwd(), 'test-results', 'test-summary.json');
    
    const summary = {
      timestamp: new Date().toISOString(),
      environment: {
        nodeVersion: process.version,
        platform: process.platform,
        arch: process.arch,
      },
      testRun: {
        startTime: process.env.TEST_START_TIME || new Date().toISOString(),
        endTime: new Date().toISOString(),
        duration: Date.now() - (parseInt(process.env.TEST_START_TIMESTAMP || '0') || Date.now()),
      },
      configuration: {
        testEnvironment: process.env.NODE_ENV,
        coverage: process.env.COVERAGE_ENABLED === 'true',
        ci: process.env.CI === 'true',
      },
    };

    await fs.writeFile(summaryPath, JSON.stringify(summary, null, 2));
    console.log('📊 Test summary generated at test-results/test-summary.json');
  } catch (error) {
    console.warn('⚠️ Could not generate test summary:', error);
  }
}

export default globalTeardown;