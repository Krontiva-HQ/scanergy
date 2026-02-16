# Scarnergy — API Reference

> **Base URL**: `http://localhost:3001/rest/v1` (Supabase PostgREST)
> **Auth**: Bearer JWT token in Authorization header
> **Format**: JSON request/response

---

## 1. Authentication

### Login
```bash
curl -X POST http://localhost:3001/auth/v1/token?grant_type=password \
  -H "apikey: $ANON_KEY" \
  -H "Content-Type: application/json" \
  -d '{"email":"inspector@krontiva.com","password":"password123"}'

# Response: { "access_token": "eyJ...", "refresh_token": "...", "user": {...} }
```

## 2. Objects (Buildings)

### List Objects
```bash
curl "http://localhost:3001/rest/v1/objects?select=*&status=eq.pending&order=opname_datum.asc" \
  -H "Authorization: Bearer $TOKEN" \
  -H "apikey: $ANON_KEY"
```

### Get Object with Zones
```bash
curl "http://localhost:3001/rest/v1/objects?select=*,rekenzones(*,gevels(*),daken(*),vloeren(*),installaties(*))&id=eq.$OBJECT_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "apikey: $ANON_KEY"
```

### Create Object
```bash
curl -X POST "http://localhost:3001/rest/v1/objects" \
  -H "Authorization: Bearer $TOKEN" \
  -H "apikey: $ANON_KEY" \
  -H "Content-Type: application/json" \
  -d '{"adres":"Keizersgracht 100","postcode":"1015AA","plaats":"Amsterdam","building_type":"residential"}'
```

## 3. Measurements

### Submit Measurement (Single)
```bash
curl -X POST "http://localhost:3001/rest/v1/measurements" \
  -H "Authorization: Bearer $TOKEN" \
  -H "apikey: $ANON_KEY" \
  -H "Content-Type: application/json" \
  -d '{"value_mm":2450,"source":"ble_mobile","device_id":"uuid","session_id":"uuid","element_type":"gevel","element_id":"uuid","captured_at":"2026-02-11T14:30:00Z"}'
```

### Submit Batch (Edge Function)
```bash
curl -X POST "http://localhost:54321/functions/v1/measurement-ingest" \
  -H "Authorization: Bearer $SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"measurements":[{"value_mm":2450,...},{"value_mm":4800,...}]}'
```

### Query Measurements (Time Range)
```bash
curl "http://localhost:3001/rest/v1/measurements?session_id=eq.$SESSION_ID&captured_at=gte.2026-02-11T00:00:00Z&order=captured_at.desc" \
  -H "Authorization: Bearer $TOKEN" \
  -H "apikey: $ANON_KEY"
```

## 4. Real-Time Subscriptions

### WebSocket (Supabase Realtime)
```javascript
const channel = supabase
  .channel('measurements')
  .on('postgres_changes', {
    event: 'INSERT',
    schema: 'public',
    table: 'measurements',
    filter: `session_id=eq.${sessionId}`
  }, (payload) => console.log('New measurement:', payload.new))
  .subscribe();
```

## 5. AI Engine

### Validate Measurement
```bash
curl -X POST "http://localhost:8500/validate" \
  -H "Content-Type: application/json" \
  -d '{"value_mm":2450,"element_type":"gevel","measurement_rate":1.0,"time_since_last":5.0,"session_mean":3500,"session_std":500}'

# Response: {"is_anomaly":false,"anomaly_score":0.85,"measurement_type":"wall_height","confidence":0.92,"flags":[]}
```

### Predict Energy Label
```bash
curl -X POST "http://localhost:8500/predict-energy" \
  -H "Content-Type: application/json" \
  -d '{"object_id":"uuid"}'

# Response: {"energy_label":"C","energy_index":1.35,"confidence":0.78}
```

## 6. WebSocket (BLE Bridge)

### Connect
```javascript
const ws = new WebSocket('ws://localhost:8765');
ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  if (msg.type === 'measurement') {
    console.log(`${msg.value_mm}mm from ${msg.device_id}`);
  }
};
```

### Send Command
```javascript
ws.send(JSON.stringify({
  type: 'command',
  action: 'reconnect_device',
  device_address: 'AA:BB:CC:DD:EE:FF'
}));
```

---

*This document is confidential and intended for Krontiva Africa internal use only.*
