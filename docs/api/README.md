# LUKHAS API Usage Guide

Welcome to the LUKHAS API! This guide provides a high-level overview of the API, including how to get started, our versioning strategy, and information on rate limiting. For detailed information about each endpoint, please refer to the [OpenAPI Specification](openapi_spec.yaml).

## Getting Started

To get started with the LUKHAS API, you will need to obtain an API key or an OAuth2 bearer token. Please refer to the [Authentication Guide](authentication.md) for detailed instructions on how to authenticate with the API.

Once you have your credentials, you can start making requests to the API. The base URL for the API is `https://api.lukhas.ai` for production and `http://localhost:8000` for local development.

Here is an example of how to make a request to the `/v1/models` endpoint using `curl`:

```bash
curl -X GET "https://api.lukhas.ai/v1/models" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

## API Versioning

The LUKHAS API uses a versioning scheme to ensure that changes to the API are introduced in a backward-compatible manner. The current version of the API is v1. The API version is included in the URL of each endpoint (e.g., `/v1/models`).

When we introduce breaking changes to the API, we will release a new version of the API. We will provide a migration guide to help you transition to the new version.

## Rate Limiting

To ensure the stability and availability of the LUKHAS API, we have implemented rate limiting. The rate limits are applied on a per-user basis. The current rate limit is 60 requests per minute.

When you exceed the rate limit, the API will return a `429 Too Many Requests` error. The response will include a `Retry-After` header that indicates how many seconds you should wait before making another request.

The following headers are included in each response to help you track your rate limit usage:

- `X-RateLimit-Limit`: The maximum number of requests you are allowed to make in a 60-second window.
- `X-RateLimit-Remaining`: The number of requests you have remaining in the current window.
- `X-RateLimit-Reset`: The time at which the current rate limit window will reset, in UTC epoch seconds.
