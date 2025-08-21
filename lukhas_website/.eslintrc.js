module.exports = {
  extends: ['next/core-web-vitals'],
  plugins: ['./tools/eslint-plugin-lukhas'],
  rules: {
    // Warn only to maintain dev velocity
    'lukhas/require-transparency-box': 'warn',
    
    // Your existing rules can go here
    'react/no-unescaped-entities': 'off',
    '@next/next/no-page-custom-font': 'off'
  }
};