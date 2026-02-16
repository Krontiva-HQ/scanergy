# Architecture — Expo App

## Overview

- Entry is via [index.ts](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/index.ts), which registers [App.tsx](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/App.tsx).
- App composes:
  - [MeasurementProvider.tsx](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/measurement/MeasurementProvider.tsx): context provider for measurement state.
  - [HomeScreen.tsx](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/HomeScreen.tsx): main navigation with three tabs (list, calendar, measurements).

## UI Screens

- Home Screen:
  - Loads sample data at startup via `applyDataOverride`.
  - Renders list of objects, calendar of placeholder visits, and measurement dashboard.
- Object Detail:
  - [ObjectDetailScreen.tsx](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/ObjectDetailScreen.tsx) shows related rekenzones, gevels, daken, vloeren, and installaties.
  - Provides inline forms (e.g., [GevelForm.tsx](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/GevelForm.tsx), [DakForm.tsx](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/DakForm.tsx), [InstallatieForm.tsx](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/InstallatieForm.tsx)).
- Gevel & Dak Details:
  - [GevelDetailScreen.tsx](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/GevelDetailScreen.tsx)
  - [DakDetailScreen.tsx](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/DakDetailScreen.tsx)

## Data Layer

- Sample Data:
  - [sampleData.ts](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/sampleData.ts) defines seeded arrays for Objecten, Rekenzones, Vloeren, Gevels, Daken, Installaties, etc.
- In-Memory Store:
  - [queries.ts](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/queries.ts) holds in-memory arrays and relation helpers (e.g., `getRekenzonesForObjectLocal`).
  - `applyDataOverride` updates arrays atomically with provided datasets.
- App Mode:
  - [appMode.ts](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/appMode.ts) tracks current mode value; UI toggles remain in the app bar for future expansion.

## Measurement Integration

- WebSocket Hook:
  - [useWebSocket.ts](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/hooks/useWebSocket.ts) manages websocket connection to Python.
- UI:
  - [MeasurementDashboard.tsx](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/MeasurementDashboard.tsx) shows status, devices, and basic stats.
- Types & Utils:
  - [measurement/types.ts](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/measurement/types.ts)
  - [measurement/utils.ts](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/measurement/utils.ts)

## Configuration & Permissions

- App config:
  - [app.json](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/app.json) includes BLE-related permissions and platform config.
- Settings:
  - [settings.ts](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/settings.ts)

## Optional AppSheet Integration

- Existing integration stubs:
  - [appsheetApi.ts](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/appsheetApi.ts): REST calls to AppSheet Action endpoints.
  - [appsheetAdapter.ts](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/appsheetAdapter.ts): mapping AppSheet rows to local types.
- Current state:
  - Disabled for this build; HomeScreen uses sample data exclusively.

## Scripts
 
 - See [package.json](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/package.json) for `start`, `ios`, `android`, `web`, and Python helpers.
 
 ## Data Orchestration (Xano)
 
 - Orchestrator: Xano hosts REST endpoints for domain data and events.
 - Read flow:
   - UI calls Xano endpoints to fetch objects, zones, and visit schedules.
   - Responses map to local types used by queries.ts.
 - Write flow:
   - UI and Python bridge post measurement and inspection events to Xano.
 - Config:
   - Base URL: XANO_BASE_URL
   - Auth: XANO_API_KEY or JWT; keep secrets out of the repo and use env vars.
 - Migration plan:
   - Implement xanoApi service to replace AppSheet calls.
   - Map Xano payloads to local types, then inject via applyDataOverride or state.
