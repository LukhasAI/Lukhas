# LUKHAS AI with the OpenAI Compatibility Layer

**Last Updated**: 2025-11-08


This guide explains how to use the LUKHAS AI API's OpenAI compatibility layer.

## OpenAI Compatibility Layer

The LUKHAS AI API provides an OpenAI-compatible endpoint for chat completions. This allows you to use the LUKHAS AI with existing tools and libraries that are designed to work with the OpenAI API.

## Migration from OpenAI

To migrate from the OpenAI API to the LUKHAS AI API, you'll need to make the following changes to your code:

1.  **Change the base URL:** The base URL for the OpenAI-compatible endpoint is `https://api.lukhas.ai/v1/openai`.
2.  **Use your LUKHAS AI API key:** You'll need to use your LUKHAS AI API key to authenticate your requests.

## Feature Comparison

| Feature | OpenAI | LUKHAS AI |
|---|---|---|
| Chat Completions | Yes | Yes |
| Embeddings | Yes | No |
| Fine-tuning | Yes | No |

## Drop-in Replacement Examples

### Python

```python
import openai

openai.api_base = "https://api.lukhas.ai/v1/openai"
openai.api_key = "YOUR_LUKHAS_API_KEY"

response = openai.ChatCompletion.create(
    model="lukhas-consciousness-1",
    messages=[
        {"role": "user", "content": "Hello, LUKHAS!"}
    ]
)

print(response.choices[0].message.content)
```
