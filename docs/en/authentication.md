# Authentication

## Development Mode

Auth is disabled by default. Run the server and use the API directly without a key.

---

## Production Mode

### 1. Enable authentication

In `config.yaml`:

```yaml
app:
  mode: production
security:
  auth_enabled: true
```

### 2. Get an API key

```bash
curl -X POST https://islam-mate-api.readthedocs.io/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Your Name", "email": "your@email.com"}'
```

Response:

```json
{
  "message": "API key generated successfully",
  "api_key": "im_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "warning": "Save this key - it will not be shown again"
}
```

!!! warning "Warning"
    Save your key immediately. It will not be shown again.

### 3. Use your key

```bash
curl https://islam-mate-api.readthedocs.io/api/v1/hadith/bukhari/1 \
  -H "X-API-Key: im_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

---

## Response Codes

| Code | Meaning |
|---|---|
| 200 | Success |
| 401 | API key required |
| 403 | Invalid API key |
| 429 | Rate limit exceeded |
