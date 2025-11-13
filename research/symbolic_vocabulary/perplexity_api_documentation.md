# Perplexity API Documentation Summary

## Available Models
- **sonar**: Lightweight search model with grounding
- **sonar-pro**: Advanced search offering with grounding, supporting complex queries
- **sonar-deep-research**: Expert-level research model conducting exhaustive searches and generating comprehensive reports
- **sonar-reasoning**: Fast, real-time reasoning model designed for problem-solving with search
- **sonar-reasoning-pro**: Precise reasoning offering powered by DeepSeek-R1 with Chain of Thought (CoT)

## API Endpoint
```
POST https://api.perplexity.ai/chat/completions
```

## Authentication
```
Authorization: Bearer <token>
```

## Request Format
```json
{
  "model": "sonar-deep-research",
  "messages": [
    {
      "role": "system",
      "content": "Be precise and concise."
    },
    {
      "role": "user", 
      "content": "Your question here"
    }
  ],
  "search_mode": "web|academic|sec",
  "reasoning_effort": "low|medium|high",
  "max_tokens": 4000,
  "temperature": 0.2,
  "return_related_questions": true,
  "return_images": false
}
```

## Best Model for Our Research
**sonar-deep-research** - Expert-level research model conducting exhaustive searches and generating comprehensive reports. Perfect for our symbolic vocabulary research.