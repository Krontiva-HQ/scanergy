# Data Model — Expo App

## Core Types

Defined in [types.ts]:
- ObjectRecord: basic object meta (adres, postcode, opnameDatum, status, inspecteurId)
- Rekenzone: per-object zone grouping (naam, related IDs)
- Gevel: facade info (positie, berekendeOrientatie, afmetingen, flags)
- Dak: roof info (typeDak, hoek, oppervlakte fields)
- Vloer: floor info (isolatie flags, oppervlakte, perimeter fields)
- Installatie: equipment info (typeInstallatie, merkModel, locatie)

Measurement types live under:
- [measurement/types.ts]

## Sample Data

Seeded arrays are in [sampleData.ts]:
- `objecten`, `rekenzones`, `gevels`, `daken`, `vloeren`, `installaties`, plus `contactpersonen`, `inspecteurs`, etc.
- Designed for offline UI usage and quick demos.

## In-Memory Store & Queries

- [queries.ts](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/queries.ts) maintains in-memory arrays and exposes helpers:
  - `getObjectById`, `getAllObjectsLocal`
  - `getRekenzonesForObjectLocal`
  - `getGevelsForRekenzoneLocal`, `getDakenForRekenzoneLocal`, `getVloerenForRekenzoneLocal`, `getInstallatiesForRekenzoneLocal`
 - Data injection:
  - `applyDataOverride({...})` replaces the in-memory arrays with provided datasets atomically.
 
 ## Xano Contracts
 
 - Orchestrator handles domain storage and events.
 - Typical endpoints (examples; replace with your workspace URLs):
   - GET /objects
   - GET /objects/{id}
   - GET /objects/{id}/rekenzones
   - GET /calendar/visits?from=YYYY-MM-DD&to=YYYY-MM-DD
   - POST /measurements
   - POST /inspections
 - Mapping:
   - Align Xano field names to local types in types.ts.
   - Convert missing/extra fields in a thin adapter before calling applyDataOverride.
 - Auth:
   - Use XANO_API_KEY or JWT in Authorization header.
   - Do not commit secrets; load from environment/config.

