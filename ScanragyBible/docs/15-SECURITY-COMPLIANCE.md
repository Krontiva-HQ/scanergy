# Scarnergy — Security & Compliance

> **Auth**: Supabase Auth (GoTrue) — JWT-based
> **Authorization**: PostgreSQL Row-Level Security (RLS)
> **Encryption**: TLS 1.3 in transit, AES-256 at rest
> **Compliance**: GDPR, Dutch privacy regulations

---

## 1. Authentication Flow

```
Mobile App                      Supabase Auth (GoTrue)
    │                                   │
    ├─ POST /auth/v1/token ────────────►│
    │  {email, password}                │
    │                                   ├─ Verify credentials
    │◄──────────────────────────────────┤
    │  {access_token, refresh_token}    │
    │                                   │
    ├─ GET /rest/v1/objects ───────────►│
    │  Authorization: Bearer {jwt}      │
    │                                   ├─ Verify JWT
    │                                   ├─ Extract user.id, org_id
    │                                   ├─ Apply RLS policies
    │◄──────────────────────────────────┤
    │  {filtered data for user's org}   │
```

## 2. Row-Level Security Policies

```sql
-- Objects: users can only see their organization's buildings
CREATE POLICY "org_isolation" ON objects
  FOR ALL USING (org_id = (SELECT org_id FROM users WHERE id = auth.uid()));

-- Measurements: inspectors see their own + supervisor sees all in org
CREATE POLICY "measurement_access" ON measurements
  FOR SELECT USING (
    org_id = (SELECT org_id FROM users WHERE id = auth.uid())
    AND (
      inspector_id = auth.uid()
      OR EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role IN ('supervisor', 'admin'))
    )
  );

-- Devices: org-scoped access
CREATE POLICY "device_access" ON devices
  FOR ALL USING (org_id = (SELECT org_id FROM users WHERE id = auth.uid()));
```

## 3. MQTT Security

| Layer | Control |
|-------|---------|
| Transport | TLS 1.3 on port 8883 |
| Authentication | Username/password per device |
| Authorization | ACL: devices publish to own topics only |
| Rate Limiting | 100 messages/minute per device |

## 4. Mobile Security

| Concern | Mitigation |
|---------|-----------|
| API keys in bundle | Use Supabase anon key (safe for client); secrets in Edge Functions only |
| BLE sniffing | Measurement data is not sensitive; device pairing is proximity-based |
| Offline data | MMKV encrypted storage on device |
| Photo upload | Signed URLs for Supabase Storage; HTTPS only |

---

*This document is confidential and intended for Krontiva Africa internal use only.*
