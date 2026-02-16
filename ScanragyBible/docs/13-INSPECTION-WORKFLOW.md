# Scarnergy — Inspection Workflow

> **Lifecycle**: Schedule → Assign → Inspect → Validate → Report → Complete
> **Actors**: Supervisor (schedule/assign/review), Inspector (measure/capture), System (validate/compute)

---

## 1. Workflow States

```
SCHEDULED ──► ASSIGNED ──► IN_PROGRESS ──► CAPTURED ──► VALIDATED ──► REPORTED ──► COMPLETE
    │              │             │               │            │             │
    └─ CANCELLED   └─ REASSIGNED └─ PAUSED       └─ FLAGGED   └─ REJECTED  └─ ARCHIVED
```

## 2. Inspector Field Process

1. **Arrive**: Open mobile app → Select today's building from calendar
2. **Survey**: Walk building exterior → Identify zones, facades, roof types
3. **Measure**: For each element:
   - Open element form (Gevel/Dak/Vloer)
   - Tap "📡" on measurement fields
   - Point Bosch GLM at surface → Press measure button
   - Value auto-fills in form with AI validation indicator
4. **Photo**: Capture inspection photos for each element
5. **Review**: Review all captured data, resolve any anomaly flags
6. **Submit**: Sync all data to Supabase → Trigger report generation

## 3. Report Generation

```
Inspector submits ──► Edge Function triggered ──► Fetch all building data
                                                        │
                     PDF delivered to ◄── WeasyPrint ◄── Jinja2 template
                     Supabase Storage                    + chart images
                         │
                    Mobile app shows ◄── Download link
                    Supervisor review
```

---

*This document is confidential and intended for Krontiva Africa internal use only.*
