# Rate Limiting

## Default Limit

- **60 requests per minute** per IP address
- Counter resets every 60 seconds

---

## Exceeded Limit Response

```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Limit: 60 per minute",
  "retry_after": "60 seconds"
}
```

HTTP Status: **429 Too Many Requests**

---

## Configuration

In `config.yaml`:

```yaml
security:
  rate_limiting: true
```

Disable in development:

```yaml
security:
  rate_limiting: false
```
