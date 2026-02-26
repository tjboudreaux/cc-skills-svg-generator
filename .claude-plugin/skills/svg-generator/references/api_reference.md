# Quiver AI API Reference

Base URL: `https://api.quiver.ai`

## Authentication

All requests require a Bearer token in the `Authorization` header:

```
Authorization: Bearer <API_KEY>
```

## Endpoints

### POST /v1/svgs/generations

Generate SVG images from text prompts.

**Request Body:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | Yes | — | Text description of the desired SVG |
| `model` | string | No | `arrow-preview` | Model to use for generation |
| `instructions` | string | No | — | Style guidance or constraints |
| `references` | array | No | — | Reference images (max 4). Each item: `ImageInputReference` |
| `n` | integer | No | 1 | Number of SVGs to generate (1-16) |
| `temperature` | number | No | 1 | Randomness control (0-2). Lower = more deterministic |
| `stream` | boolean | No | false | Enable streaming response |

**ImageInputReference format:**

```json
{ "url": "https://example.com/image.png" }
```

or with base64:

```json
{ "url": "data:image/png;base64,iVBOR..." }
```

---

### POST /v1/svgs/vectorizations

Convert raster images (PNG, JPG, WebP, etc.) to SVG vector format.

**Request Body:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `image` | object | Yes | — | Image to vectorize. Format: `{"url": "..."}` (URL or base64 data URI) |
| `model` | string | No | `arrow-preview` | Model to use for vectorization |
| `auto_crop` | boolean | No | false | Automatically crop whitespace/background |
| `target_size` | integer | No | — | Target output size in pixels (128-4096) |
| `n` | integer | No | 1 | Number of SVGs to generate (1-16) |
| `temperature` | number | No | 1 | Randomness control (0-2) |
| `stream` | boolean | No | false | Enable streaming response |

**Image input format (URL):**

```json
{ "image": { "url": "https://example.com/photo.png" } }
```

**Image input format (base64):**

```json
{ "image": { "url": "data:image/png;base64,iVBOR..." } }
```

---

## Response Format

Both endpoints return the same response structure:

```json
{
  "id": "svg_abc123",
  "created": 1700000000,
  "data": [
    {
      "svg": "<svg xmlns=\"http://www.w3.org/2000/svg\" ...>...</svg>",
      "mime_type": "image/svg+xml"
    }
  ],
  "usage": {
    "prompt_tokens": 150,
    "completion_tokens": 500,
    "total_tokens": 650
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique request identifier |
| `created` | integer | Unix timestamp of creation |
| `data` | array | Array of generated SVGs |
| `data[].svg` | string | The SVG markup |
| `data[].mime_type` | string | Always `image/svg+xml` |
| `usage` | object | Token usage statistics |

---

## Streaming Response

When `stream: true`, the API returns Server-Sent Events (SSE):

```
data: {"type": "content_block_delta", "delta": {"svg_chunk": "..."}}

data: {"type": "message_stop", "usage": {...}}
```

**Note:** The provided scripts do not use streaming. This is documented for reference only.

---

## Error Codes

| Status | Meaning | Common Causes |
|--------|---------|---------------|
| 400 | Bad Request | Invalid parameters, missing required fields |
| 401 | Unauthorized | Invalid or missing API key |
| 402 | Payment Required | Insufficient credits or billing issue |
| 403 | Forbidden | API key lacks permission for this endpoint |
| 404 | Not Found | Invalid endpoint URL |
| 429 | Too Many Requests | Rate limit exceeded — retry after backoff |
| 500 | Internal Server Error | Server-side issue — retry |
| 502 | Bad Gateway | Upstream service unavailable — retry |
| 503 | Service Unavailable | Maintenance or overload — retry later |

Error responses include a JSON body:

```json
{
  "error": {
    "message": "Description of the error",
    "type": "invalid_request_error",
    "code": "invalid_parameter"
  }
}
```

---

## Rate Limits

Rate limits vary by plan. When rate-limited (429), use exponential backoff. The `Retry-After` header may indicate when to retry.

## Supported Image Formats (for vectorization)

PNG, JPEG, WebP, BMP, TIFF, GIF (first frame).
