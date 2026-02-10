# Types — Domain and Measurements

## Overview

This document summarizes the core TypeScript types used by the Expo app for domain modeling and measurements, with references to the source definitions.

## Sources

- Domain types: [react-native/expo-app/src/types.ts](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/types.ts)
- Alternate model set: [react-native/expo54/types.ts](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo54/types.ts)
- Measurement types: [react-native/expo-app/src/measurement/types.ts](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/measurement/types.ts)

## Primitive Aliases

- ID: string identifiers for entities
- DateString: ISO date (YYYY-MM-DD)
- TimeString: time string (HH:mm:ss)
- DateTimeString: ISO datetime

## Domain Entities

- ObjectRecord
  - Address, schedule (opnameDatum/opnameTijd), status, inspecteur relations
  - Relations: rekenzoneIds, verdiepingIds, bagDataIds
- Rekenzone
  - Per-object grouping for envelope and system elements; holds IDs for daken, gevels, vloeren, installaties
- Gevel
  - Position/orientation, dimensions (hoogte, breedte), area, adjacency code, transparent parts
  - Flags: perimeter, berekenVlaggen; cached fields: cachedRekenhoogte, cachedRekenbreedte
- Dak
  - Type, orientation, slope (hoek), dimensions, gross/net areas
  - Relations: dakkapelIds, transparanteDeelIds
- Vloer
  - Insulation flags, area, perimeter, adjacency/orientatie codes, transparent parts, notes
- TransparanteDeel
  - Openings in gevel/dak/vloer; dimensions, count; optional photos and material/glas fields; gross/net areas
- Dakkapel
  - Dormer attributes and computed opening area; relation to gevels as needed
- Installatie
  - Equipment type, model, location, optional photos
- Inspecteur, Bedrijf, Contactpersoon
  - Basic identity and relationships (e.g., relatedObjectIds)
- BagData
  - BAG fields: IDs and address metadata
- Logic Tables
  - OrientatieLogica: orientation mapping codes and labels
  - PositieRotatieLogica: rotational position mapping
  - GrenstAanLogica: adjacency codes and affected element IDs
  - HellingshoekLogica: slope codes
  - ZonweringLogica: shading devices and relationships
- Helpers
  - HomeListItem: list representation for UI sections and dates

## Computed and Derived Fields

- Geometries
  - brutoOppervlakte: gross area (length × width), often defaulted if not provided
  - nettoDakoppervlak and nettoOppervlakte: net areas after subtracting openings
  - oppervlakteGat: opening area for dakkapellen/transparante delen
  - perimeterBerekend/totalePerimeter: floor edge aggregates
  - Cached dimensions: cachedRekenhoogte/cachedRekenbreedte store adjusted values for gevels
- Orientation/Slope
  - berekendeOrientatie and orientatieCode capture cardinal direction and code
  - hoek in roofs for slope
- Relations
  - *_Ids arrays connect entities; used for fast local joins in queries.ts

## Measurements

- MeasurementData
  - value (mm), timestamp, rawHex, optional formatted string
- MeasurementStats
  - count, average, min/max, range, standardDeviation
- ConnectionStatus
  - connected, pythonScriptRunning, streaming, lastConnected, error
- MeasurementUnit and MeasurementOptions
  - Unit selection (mm/cm/m/in/ft), precision, display preferences
- WebSocketMessage
  - message envelope with type and payload
- DeviceInfo
  - name, address, connected, lastSeen metadata

## Integration Notes

- Types underpin forms and details:
  - Gevel/Dak/Vloer/Installatie forms read/write fields and trigger recalculations
- queries.ts holds in‑memory arrays and relation helpers; `applyDataOverride` swaps datasets atomically
- Measurement types support the dashboard and live capture UI via WebSockets

## References in UI

- Forms and detail screens:
  - GevelForm: [react-native/expo-app/src/GevelForm.tsx](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/GevelForm.tsx)
  - DakForm: [react-native/expo-app/src/DakForm.tsx](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/DakForm.tsx)
  - InstallatieForm: [react-native/expo-app/src/InstallatieForm.tsx](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/InstallatieForm.tsx)
  - GevelDetailScreen: [react-native/expo-app/src/GevelDetailScreen.tsx](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/GevelDetailScreen.tsx)
  - DakDetailScreen: [react-native/expo-app/src/DakDetailScreen.tsx](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/DakDetailScreen.tsx)
