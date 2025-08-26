// API Keys Configuration
// ⚠️ IMPORTANT: This file should NOT be committed to version control
// Add this file to your .gitignore

// Copy this file to api-keys.js and add your actual API keys
const APIKeys = {
    // OpenAI API Key (get from: https://platform.openai.com/api-keys)
    openai: 'sk-your-openai-api-key-here',

    // Claude API Key (get from: https://console.anthropic.com/)
    claude: 'sk-ant-your-claude-api-key-here',

    // Azure OpenAI API Key (get from: https://portal.azure.com/)
    azure: 'your-azure-openai-api-key-here',

    // Google Gemini API Key (get from: https://makersuite.google.com/app/apikey)
    gemini: 'your-gemini-api-key-here',

    // Perplexity API Key (get from: https://www.perplexity.ai/settings/api)
    perplexity: 'your-perplexity-api-key-here',
};

// Export for use in elite-config.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = APIKeys;
} else {
    window.APIKeys = APIKeys;
}

// Instructions:
// 1. Replace the placeholder values with your actual API keys
// 2. Add this file to your .gitignore to keep keys secure
// 3. In elite-config.js, import this file and use: apiKeys: APIKeys
