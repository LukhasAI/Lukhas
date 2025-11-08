# Getting Started with the LUKHAS AI API

**Last Updated**: 2025-11-08


This guide will walk you through the basics of using the LUKHAS AI API.

## Quick Start (5 minutes)

1.  **Get your API key:** You'll need an API key to authenticate your requests. You can find your API key in your LUKHAS AI account settings.
2.  **Make your first API call:** Use the following `curl` command to make a simple request to the Consciousness Chat API:

    ```bash
    curl -X POST "https://api.lukhas.ai/v1/chat" \
         -H "Authorization: Bearer YOUR_API_KEY" \
         -H "Content-Type: application/json" \
         -d '{
           "message": "Hello, LUKHAS!"
         }'
    ```

## Installation

The LUKHAS AI API is a RESTful API, so you can use any HTTP client to interact with it. The examples in this documentation use `curl` and the Python `requests` library.

To install the Python `requests` library, run the following command:

```bash
pip install requests
```

## Authentication

All API requests must be authenticated with an API key. You can do this by including an `Authorization` header with your API key as a Bearer token:

```
Authorization: Bearer YOUR_API_KEY
```

## Common Use Cases

*   **Natural Language Interaction:** Use the Consciousness Chat API to have conversations with the LUKHAS AI.
*   **User Feedback:** Collect user feedback on AI responses using the Feedback API.
*   **Identity Management:** Manage user identities with the Identity API.
*   **Ethical Oversight:** Monitor the ethical performance of the AI with the Guardian API.

## Troubleshooting

*   **401 Unauthorized:** Make sure you're including your API key in the `Authorization` header.
*   **400 Bad Request:** Check that your request body is valid JSON.
*   **500 Internal Server Error:** If you're consistently seeing this error, please contact support.
