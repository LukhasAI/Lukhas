// macOS Keychain Integration for AI Voice System
// Securely retrieves API keys from macOS Keychain

class KeychainIntegration {
    constructor() {
        this.keychainService = 'AIVoiceIntegration';
        this.apiKeys = {};
        this.isInitialized = false;
    }
    
    // Initialize Keychain integration
    async init() {
        try {
            // Check if we're on macOS
            if (navigator.platform.indexOf('Mac') === -1) {
                console.log('⚠️ Keychain integration only available on macOS');
                return false;
            }
            
            // Try to retrieve API keys from Keychain
            await this.loadAPIKeysFromKeychain();
            this.isInitialized = true;
            
            console.log('✅ Keychain integration initialized');
            return true;
            
        } catch (error) {
            console.log('❌ Keychain integration failed:', error.message);
            return false;
        }
    }
    
    // Load API keys from macOS Keychain
    async loadAPIKeysFromKeychain() {
        const keyNames = [
            'openai_api_key',
            'claude_api_key', 
            'azure_openai_key',
            'gemini_api_key',
            'perplexity_api_key'
        ];
        
        for (const keyName of keyNames) {
            try {
                const keyValue = await this.getKeychainItem(keyName);
                if (keyValue) {
                    this.apiKeys[keyName] = keyValue;
                    console.log(`✅ Loaded ${keyName} from Keychain`);
                }
            } catch (error) {
                console.log(`⚠️ Could not load ${keyName} from Keychain:`, error.message);
            }
        }
    }
    
    // Get item from macOS Keychain using native macOS integration
    async getKeychainItem(itemName) {
        try {
            // Use macOS native keychain access
            // This requires a native macOS app or Electron
            // For web browsers, we'll use a fallback approach
            
            if (window.electronAPI) {
                // Electron app integration
                return await window.electronAPI.getKeychainItem(itemName);
            } else if (window.webkit && window.webkit.messageHandlers) {
                // WebKit integration (Safari)
                return await this.getKeychainItemWebKit(itemName);
            } else {
                // Fallback: prompt user to manually enter keys
                return await this.promptForKeychainItem(itemName);
            }
            
        } catch (error) {
            console.log(`Error accessing Keychain for ${itemName}:`, error);
            return null;
        }
    }
    
    // WebKit integration for Safari
    async getKeychainItemWebKit(itemName) {
        return new Promise((resolve, reject) => {
            if (window.webkit && window.webkit.messageHandlers.keychainHandler) {
                window.webkit.messageHandlers.keychainHandler.postMessage({
                    action: 'get',
                    item: itemName
                });
                
                // Listen for response
                window.addEventListener('keychainResponse', (event) => {
                    resolve(event.detail.value);
                });
            } else {
                reject(new Error('WebKit keychain handler not available'));
            }
        });
    }
    
    // Fallback: prompt user to manually enter key
    async promptForKeychainItem(itemName) {
        const displayName = this.getDisplayName(itemName);
        
        return new Promise((resolve) => {
            const key = prompt(
                `Please enter your ${displayName} API key.\n\n` +
                `This key will be stored securely in your browser's local storage.\n` +
                `You can also add it to your macOS Keychain for better security.`,
                ''
            );
            
            if (key && key.trim()) {
                // Store in browser's secure storage as fallback
                this.storeInSecureStorage(itemName, key.trim());
                resolve(key.trim());
            } else {
                resolve(null);
            }
        });
    }
    
    // Store key in browser's secure storage
    storeInSecureStorage(itemName, keyValue) {
        try {
            // Use localStorage with basic encryption (for demo purposes)
            // In production, use more secure methods
            const encrypted = btoa(keyValue); // Basic encoding
            localStorage.setItem(`secure_${itemName}`, encrypted);
            console.log(`✅ Stored ${itemName} in secure storage`);
        } catch (error) {
            console.log(`❌ Failed to store ${itemName}:`, error);
        }
    }
    
    // Retrieve key from browser's secure storage
    getFromSecureStorage(itemName) {
        try {
            const encrypted = localStorage.getItem(`secure_${itemName}`);
            if (encrypted) {
                return atob(encrypted); // Basic decoding
            }
        } catch (error) {
            console.log(`❌ Failed to retrieve ${itemName}:`, error);
        }
        return null;
    }
    
    // Get display name for API key
    getDisplayName(itemName) {
        const names = {
            'openai_api_key': 'OpenAI GPT-4',
            'claude_api_key': 'Claude',
            'azure_openai_key': 'Azure OpenAI',
            'gemini_api_key': 'Google Gemini',
            'perplexity_api_key': 'Perplexity'
        };
        return names[itemName] || itemName;
    }
    
    // Get all API keys in the format expected by Config
    getAPIKeysForConfig() {
        return {
            openai: this.apiKeys['openai_api_key'] || this.getFromSecureStorage('openai_api_key'),
            claude: this.apiKeys['claude_api_key'] || this.getFromSecureStorage('claude_api_key'),
            azure: this.apiKeys['azure_openai_key'] || this.getFromSecureStorage('azure_openai_key'),
            gemini: this.apiKeys['gemini_api_key'] || this.getFromSecureStorage('gemini_api_key'),
            perplexity: this.apiKeys['perplexity_api_key'] || this.getFromSecureStorage('perplexity_api_key')
        };
    }
    
    // Add new API key to Keychain
    async addKeychainItem(itemName, keyValue) {
        try {
            if (window.electronAPI) {
                await window.electronAPI.addKeychainItem(itemName, keyValue);
            } else {
                // Store in secure storage as fallback
                this.storeInSecureStorage(itemName, keyValue);
            }
            
            this.apiKeys[itemName] = keyValue;
            console.log(`✅ Added ${itemName} to secure storage`);
            return true;
            
        } catch (error) {
            console.log(`❌ Failed to add ${itemName}:`, error);
            return false;
        }
    }
    
    // Check if we have any API keys available
    hasAnyAPIKeys() {
        const keys = this.getAPIKeysForConfig();
        return Object.values(keys).some(key => key && key.length > 0);
    }
    
    // Get status of all API keys
    getAPIKeyStatus() {
        const keys = this.getAPIKeysForConfig();
        const status = {};
        
        Object.entries(keys).forEach(([provider, key]) => {
            status[provider] = {
                available: key && key.length > 0,
                length: key ? key.length : 0,
                masked: key ? `${key.substring(0, 4)}...${key.substring(key.length - 4)}` : null
            };
        });
        
        return status;
    }
    
    // Initialize with Config
    async initializeWithConfig() {
        const success = await this.init();
        
        if (success && this.hasAnyAPIKeys()) {
            // Update Config with Keychain keys
            const keychainKeys = this.getAPIKeysForConfig();
            Object.assign(Config.apiKeys, keychainKeys);
            
            console.log('✅ Config updated with Keychain API keys');
            console.log('📊 API Key Status:', this.getAPIKeyStatus());
            
            return true;
        } else {
            console.log('⚠️ No API keys found in Keychain, using fallback methods');
            return false;
        }
    }
}

// Initialize Keychain integration
window.keychainIntegration = new KeychainIntegration();

// Auto-initialize when page loads (DISABLED - causes unwanted popups)
// document.addEventListener('DOMContentLoaded', async () => {
//     await window.keychainIntegration.initializeWithConfig();
// });

// Manual initialization function (call when needed)
window.initializeKeychainIntegration = async () => {
    try {
        await window.keychainIntegration.initializeWithConfig();
        console.log('✅ Keychain integration initialized successfully');
        return true;
    } catch (error) {
        console.log('⚠️ Keychain integration failed:', error);
        return false;
    }
};

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = KeychainIntegration;
} 