# Xano — Data Orchestration

## Overview

- Xano hosts REST endpoints for domain data and inspection workflows.
- The Expo app reads objects, zones, and calendar visits from Xano.
- The Python bridge and app post measurement and inspection events to Xano.

## Configuration

- Base URL: XANO_BASE_URL
- Auth: XANO_API_KEY or JWT bearer token
- Do not commit secrets; load via environment or secure storage.

## Example Endpoints

- GET /objects
- GET /objects/{id}
- GET /objects/{id}/rekenzones
- GET /calendar/visits?from=YYYY-MM-DD&to=YYYY-MM-DD
- POST /measurements
- POST /inspections

## Payload Mapping

- Map Xano fields to local types in react-native/expo-app/src/types.ts.
- Use a thin adapter layer to convert payloads before injecting into queries via applyDataOverride.

## Posting Measurements

- Example cURL (replace placeholders):
```bash
curl -X POST "$XANO_BASE_URL/measurements" \
  -H "Authorization: Bearer $XANO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "objectId": "<uuid>",
    "measurementMm": 1234,
    "source": "glm50c",
    "timestamp": "<ISO8601>"
  }'
```

## Migration Notes

- Replace AppSheet calls with a xanoApi service.
- Keep local sample mode for offline use; toggle via settings or env.
