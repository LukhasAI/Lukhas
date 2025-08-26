# Advanced AI Integration Setup Guide

## Quick Start (5 minutes)

### 1. Configure API Keys
Edit `config.js` and add your API keys:

```javascript
apiKeys: {
    openai: 'sk-your-openai-api-key-here',
    claude: 'sk-ant-your-claude-api-key-here',
    // Add other API keys as needed
}
```

### 2. Set Your Budgets
Configure spending limits:

```javascript
costControl: {
    dailyBudget: 5.00,    // $5 per day
    monthlyBudget: 50.00, // $50 per month
}
```

### 3. Enable Advanced Features
In `config.js`, ensure these are enabled:

```javascript
advancedFeatures: {
    enableAutoOptimization: true,
    enablePerformanceMonitoring: true,
    enableCostOptimization: true,
    enableIntelligentFallbacks: true,
}
```

### 4. Initialize the System
Add this to your HTML or JavaScript:

```javascript
// Initialize the AI system
window.aiVoiceIntegration = new AIVoiceIntegration();
```

## Advanced Configuration

### Performance Tuning
```javascript
performance: {
    maxResponseTime: 3000,    // 3 seconds timeout
    cacheExpiry: 600000,      // 10 minutes cache
    maxCacheSize: 500,        // 500 cached responses
}
```

### Voice Analysis Settings
```javascript
voiceAnalysis: {
    sampleRate: 48000,        // Higher quality audio
    fftSize: 4096,           // More detailed analysis
    emotionDetectionEnabled: true,
    speechRecognitionEnabled: true,
}
```

### AI Model Preferences
```javascript
aiModels: {
    openai: {
        primary: 'gpt-4',
        fallback: 'gpt-3.5-turbo',
        maxTokens: 200,       // More detailed responses
        temperature: 0.8,     // More creative
    }
}
```

## Testing Your Setup

### 1. Check Console for Errors
Open browser console (F12) and look for:
- ✅ "Config validation passed"
- ✅ "AI system initialized"
- ❌ Any error messages

### 2. Test Voice Input
- Allow microphone access when prompted
- Speak and watch for voice data in console
- Check if sphere responds to voice

### 3. Test AI Integration
- Set at least one API key
- Trigger AI response by speaking
- Check console for AI response logs

## Troubleshooting

### No Voice Input
- Check microphone permissions
- Ensure HTTPS (required for microphone)
- Check browser console for errors

### AI Not Responding
- Verify API keys are correct
- Check rate limits and budgets
- Look for error messages in console

### Performance Issues
- Reduce FFT size for better performance
- Enable caching
- Use cheaper AI models as fallbacks

## Advanced Features Explained

### 🚀 Intelligent Fallback System
- Automatically switches between AI providers
- Uses performance data to optimize selection
- Handles API failures gracefully

### 💰 Cost Optimization
- Tracks spending in real-time
- Switches to cheaper AIs when budget is reached
- Provides detailed cost analytics

### 📊 Performance Monitoring
- Tracks response times and success rates
- Optimizes AI selection based on performance
- Provides real-time metrics

### 🔄 Response Caching
- Caches AI responses to reduce API calls
- Intelligent cache invalidation
- Significant cost savings

## Security Best Practices

### API Key Management
- Never commit API keys to version control
- Use environment variables in production
- Rotate keys regularly

### Rate Limiting
- Set appropriate rate limits
- Monitor usage patterns
- Implement backoff strategies

### Error Handling
- Log errors for debugging
- Implement graceful degradation
- Monitor for unusual patterns

## Production Deployment

### Environment Variables
```bash
OPENAI_API_KEY=your-key
CLAUDE_API_KEY=your-key
AZURE_API_KEY=your-key
```

### Performance Optimization
- Enable compression
- Use CDN for static assets
- Implement service workers
- Enable tree shaking

### Monitoring
- Set up error tracking
- Monitor API usage
- Track performance metrics
- Set up alerts for budget limits

## Support

For issues or questions:
1. Check the browser console for error messages
2. Verify your API keys and configuration
3. Test with a single AI provider first
4. Check the README.md for detailed documentation

## Next Steps

After setup:
1. Test voice reactivity
2. Experiment with different AI models
3. Customize shape libraries
4. Add your own AI agents
5. Integrate with your applications
