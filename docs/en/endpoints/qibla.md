# Qibla Direction

## Endpoint

### GET /api/v1/qibla

Get the Qibla direction and distance to Mecca for any location.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| latitude | float | Yes | Latitude (-90 to 90) |
| longitude | float | Yes | Longitude (-180 to 180) |
| lang | string | No | Language: en or ar |

**Example:**

```bash
curl "https://islam-mate-api.readthedocs.io/api/v1/qibla?latitude=30.04&longitude=31.23"
```

**Response:**

```json
{
  "bearing": 134.5,
  "direction": "South East",
  "distance_km": 1243.7,
  "location": {
    "latitude": 30.04,
    "longitude": 31.23
  }
}
```

## How It Works

The Qibla direction is calculated using the **great-circle formula** — the shortest path between two points on a sphere.

**Kaaba coordinates:** 21.4225°N, 39.8262°E

The bearing is measured in degrees clockwise from North:
- 0° = North
- 90° = East
- 180° = South
- 270° = West

## Language Support

```bash
# English
curl "https://islam-mate-api.readthedocs.io/api/v1/en/qibla?latitude=30.04&longitude=31.23"

# Arabic
curl "https://islam-mate-api.readthedocs.io/api/v1/ar/qibla?latitude=30.04&longitude=31.23"
```
