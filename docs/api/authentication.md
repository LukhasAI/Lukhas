# LUKHAS API Authentication

The LUKHAS API uses two methods for authentication: API keys and OAuth2 bearer tokens. This guide explains how to use both methods to securely access the API.

## API Key Authentication

API Key authentication is suitable for server-to-server communication where you need to grant access to a specific application or service.

### Obtaining an API Key

To obtain an API key, please contact the LUKHAS support team. You will be provided with a unique API key that you can use to authenticate with the API.

### Using an API Key

To use an API key, you must include it in the `X-API-Key` header of each request.

Here is an example of how to make a request to the `/v1/models` endpoint using an API key:

```bash
curl -X GET "https://api.lukhas.ai/v1/models" \
     -H "X-API-Key: YOUR_API_KEY"
```

## OAuth2 Bearer Token Authentication

OAuth2 Bearer Token authentication is suitable for applications where you need to grant access to individual users.

### Obtaining a Bearer Token

To obtain a bearer token, you must first authenticate with the `/token` endpoint using your username and password. The endpoint will return an access token that you can use to authenticate with the API.

Here is an example of how to obtain a bearer token using `curl`:

```bash
curl -X POST "https://api.lukhas.ai/token" \
     -d "username=YOUR_USERNAME&password=YOUR_PASSWORD" \
     -H "Content-Type: application/x-www-form-urlencoded"
```

The response will be a JSON object containing the access token:

```json
{
  "access_token": "YOUR_ACCESS_TOKEN",
  "token_type": "bearer"
}
```

### Using a Bearer Token

To use a bearer token, you must include it in the `Authorization` header of each request, with the `Bearer` prefix.

Here is an example of how to make a request to the `/v1/models` endpoint using a bearer token:

```bash
curl -X GET "https://api.lukhas.ai/v1/models" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```
