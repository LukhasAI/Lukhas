const lukhasPlugin = require('./tools/eslint-plugin-lukhas');

module.exports = {
  extends: ['next/core-web-vitals'],
  plugins: {
    // register local plugin object (so no npm publish needed)
    lukhas: lukhasPlugin
  },
  rules: {
    // Warn only to maintain dev velocity
    'lukhas/require-transparency-box': 'warn',

    // Your existing rules can go here
    'react/no-unescaped-entities': 'off',
    '@next/next/no-page-custom-font': 'off'
  }
};
