# Scarnergy — Domain Data Model

> **Domain**: Building inspection and energy assessment
> **Language**: Dutch construction terminology (NTA 8800 standard)
> **Schema**: PostgreSQL with TimescaleDB extension

---

## 1. Entity Relationship Overview

```
Organization (1)──────(N) User
     │
     └──(N) Object (Building)
              │
              ├──(N) Rekenzone (Calculation Zone)
              │         │
              │         ├──(N) Gevel (Facade)
              │         │        └──(N) TransparanteDeel (Opening)
              │         │
              │         ├──(N) Dak (Roof)
              │         │        ├──(N) TransparanteDeel (Opening)
              │         │        └──(N) Dakkapel (Dormer)
              │         │
              │         ├──(N) Vloer (Floor)
              │         │        └──(N) TransparanteDeel (Opening)
              │         │
              │         └──(N) Installatie (Installation)
              │
              ├──(N) Inspection
              │         └──(N) MeasurementSession
              │                    └──(N) Measurement (TimescaleDB)
              │
              └──(N) CalendarVisit
```

---

## 2. Core Types (TypeScript)

```typescript
// Primitive Aliases
type ID = string;          // UUID v4
type DateString = string;  // YYYY-MM-DD
type DateTimeString = string; // ISO 8601

// Building Object
interface ObjectRecord {
  id: ID;
  org_id: ID;
  adres: string;
  postcode: string;
  plaats: string;
  latitude?: number;
  longitude?: number;
  building_type: 'residential' | 'commercial' | 'industrial' | 'mixed';
  bouwjaar?: number;
  status: 'pending' | 'in_progress' | 'complete' | 'review';
  opname_datum?: DateString;
  opname_tijd?: string;
  inspecteur_id?: ID;
  energy_label?: 'A' | 'B' | 'C' | 'D' | 'E' | 'F' | 'G';
  energy_index?: number;
  created_at: DateTimeString;
  updated_at: DateTimeString;
}

// Calculation Zone
interface Rekenzone {
  id: ID;
  object_id: ID;
  naam: string;
  verdieping: number;
  oppervlakte?: number;
  created_at: DateTimeString;
}

// Facade
interface Gevel {
  id: ID;
  rekenzone_id: ID;
  positie: string;
  berekende_orientatie?: string;
  orientatie_code?: string;
  hoogte: number;          // mm
  breedte: number;         // mm
  bruto_oppervlakte: number;  // mm² (computed: hoogte × breedte)
  netto_oppervlakte?: number; // mm² (gross - openings)
  grenst_aan_code?: string;
  is_perimeter: boolean;
  created_at: DateTimeString;
}

// Roof
interface Dak {
  id: ID;
  rekenzone_id: ID;
  type_dak: 'plat' | 'schuin' | 'zadel' | 'mansarde' | 'shed';
  hoek: number;            // degrees
  orientatie?: string;
  lengte: number;          // mm
  breedte: number;         // mm
  bruto_oppervlakte: number;
  netto_oppervlakte?: number;
  created_at: DateTimeString;
}

// Floor
interface Vloer {
  id: ID;
  rekenzone_id: ID;
  isolatie: boolean;
  isolatie_dikte?: number;  // mm
  oppervlakte: number;      // mm²
  perimeter: number;        // mm
  grenst_aan_code?: string;
  created_at: DateTimeString;
}

// Installation
interface Installatie {
  id: ID;
  rekenzone_id: ID;
  type_installatie: string;
  merk_model?: string;
  locatie?: string;
  bouwjaar?: number;
  photo_urls: string[];
  created_at: DateTimeString;
}

// Opening (in facade/roof/floor)
interface TransparanteDeel {
  id: ID;
  parent_type: 'gevel' | 'dak' | 'vloer';
  parent_id: ID;
  hoogte: number;           // mm
  breedte: number;          // mm
  aantal: number;
  bruto_oppervlakte: number; // hoogte × breedte × aantal
  materiaal?: string;
  glas_type?: string;
  created_at: DateTimeString;
}

// Measurement
interface Measurement {
  id: ID;
  value_mm: number;
  raw_hex?: string;
  source: 'ble_mobile' | 'ble_bridge' | 'mqtt_esp32' | 'manual';
  device_id?: ID;
  session_id?: ID;
  element_type?: string;
  element_id?: ID;
  inspector_id?: ID;
  org_id: ID;
  anomaly_score?: number;
  anomaly_flags?: string[];
  captured_at: DateTimeString;
}
```

---

## 3. Computed Fields

| Field | Formula | Trigger |
|-------|---------|---------|
| `gevel.bruto_oppervlakte` | `hoogte × breedte` | ON INSERT/UPDATE of gevel |
| `gevel.netto_oppervlakte` | `bruto - SUM(openings.bruto)` | ON INSERT/UPDATE/DELETE of transparante_delen |
| `dak.bruto_oppervlakte` | `lengte × breedte` | ON INSERT/UPDATE of dak |
| `dak.netto_oppervlakte` | `bruto - SUM(openings.bruto) - SUM(dakkapellen.oppervlakte)` | ON changes to children |
| `transparante_deel.bruto_oppervlakte` | `hoogte × breedte × aantal` | ON INSERT/UPDATE |

---

*This document is confidential and intended for Krontiva Africa internal use only.*
