# Bosch GLM50C Expo App — Handover Overview

This directory contains the Expo-based UI for the Bosch GLM 50C rangefinder project. It currently runs purely on built-in sample data and can optionally integrate live measurements via a Python WebSocket bridge.

## Quick Start

1. Install dependencies:
   ```bash
   cd /Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app
   npm install
   ```
2. Start the app:
   ```bash
   npm start           # Metro
   npm run ios         # iOS simulator via Expo
   npm run android     # Android emulator via Expo
   npm run web         # Expo Web + Python scripts concurrently
   ```

## Data Mode

- The app loads built-in sample data at startup and does not query AppSheet.
- Data is applied via an in-memory override using `applyDataOverride`.
- Relevant files:
  - [HomeScreen.tsx](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/HomeScreen.tsx)
  - [sampleData.ts](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/sampleData.ts)
  - [queries.ts](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/queries.ts)

To switch back to AppSheet at a later time, see the adapters in:
- [appsheetApi.ts](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/appsheetApi.ts)
- [appsheetAdapter.ts](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/appsheetAdapter.ts)

## Measurement Bridge (Python)

- Optional: run a Python WebSocket that streams measurements to the UI.
- From the Expo app directory:
  ```bash
  npm run py:ws       # start WebSocket server
  npm run py:main     # start GLM script with WebSocket updates
  npm run py:start-all
  ```
- Detailed notes: [MEASUREMENTS.md](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/MEASUREMENTS.md)

## Scripts

Defined in [package.json](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/package.json):
- `start`, `ios`, `android`, `web`
- `py:ws`, `py:main`, `py:start-all`

## Key Components

- Entry:
  - [index.ts](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/index.ts)
  - [App.tsx](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/App.tsx)
- UI:
  - [HomeScreen.tsx](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/HomeScreen.tsx)
  - [ObjectDetailScreen.tsx](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/ObjectDetailScreen.tsx)
  - [GevelDetailScreen.tsx](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/GevelDetailScreen.tsx)
  - [DakDetailScreen.tsx](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/DakDetailScreen.tsx)
- Measurement:
  - [MeasurementProvider.tsx](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/measurement/MeasurementProvider.tsx)
  - [useWebSocket.ts](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/hooks/useWebSocket.ts)

## Configuration

- App config and permissions:
  - [app.json](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/app.json)
- Local settings:
  - [settings.ts](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/settings.ts)
  - [appMode.ts](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/appMode.ts)

## Directory Structure

- Source: [src/](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src)
- Assets: [assets/](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/assets)

## Notes
 
 - BLE functionality requires a development client; see MEASUREMENTS.md for details.
 - Current UI uses sample data; network calls are inactive by design.
 
 ## Xano Integration
 
 - Orchestrates domain data and inspection events.
 - To enable Xano mode:
   - Add a xanoApi service in the app to call Xano endpoints.
   - Map responses to local types and inject via applyDataOverride/state.
   - Configure XANO_BASE_URL and XANO_API_KEY via environment.
 - Keep secrets out of the repo; use platform env/secure storage.
