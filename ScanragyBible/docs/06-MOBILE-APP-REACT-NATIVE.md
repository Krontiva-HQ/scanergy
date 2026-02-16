# Scarnergy — Mobile App (React Native / Expo)

> **Framework**: React Native with Expo (SDK 50+)  
> **Platforms**: iOS 16+ and Android 12+  
> **BLE**: react-native-ble-plx via Expo Dev Client  
> **State**: Zustand + MMKV (offline-first)  
> **Build**: EAS Build for native compilation

---

## 1. App Architecture

### Offline-First Design

```
┌─────────────────────────────────────────────────┐
│                  INSPECTOR APP                   │
│                                                  │
│  ┌─────────────────────────────────────────────┐│
│  │              UI LAYER                        ││
│  │  Screens → Components → Forms → Charts      ││
│  └────────────────┬────────────────────────────┘│
│                   │                              │
│  ┌────────────────┴────────────────────────────┐│
│  │           STATE LAYER (Zustand)              ││
│  │  measurementStore │ objectStore │ bleStore   ││
│  │  syncStore        │ settingsStore            ││
│  │                                              ││
│  │  ┌──────────────────────────────────────┐   ││
│  │  │  MMKV Persistence (Offline Queue)     │   ││
│  │  │  - Pending mutations                  │   ││
│  │  │  - Cached objects                     │   ││
│  │  │  - Measurement sessions               │   ││
│  │  └──────────────────────────────────────┘   ││
│  └────────────────┬────────────────────────────┘│
│                   │                              │
│  ┌────────────────┴────────────────────────────┐│
│  │          SERVICE LAYER                       ││
│  │  supabaseClient │ bleProtocol │ syncService ││
│  │  measurementSvc │ objectSvc   │ inspectionSvc││
│  └────────────────┬────────────────────────────┘│
│                   │                              │
│  ┌────────────────┴────────────────────────────┐│
│  │          PLATFORM LAYER                      ││
│  │  BLE (react-native-ble-plx)                 ││
│  │  Camera (expo-camera)                        ││
│  │  Location (expo-location)                    ││
│  │  TFLite (on-device ML)                      ││
│  └─────────────────────────────────────────────┘│
└─────────────────────────────────────────────────┘
```

### Navigation Structure

```
TabNavigator
├── HomeStack
│   ├── HomeScreen (Object List)
│   ├── ObjectDetailScreen
│   ├── GevelDetailScreen
│   ├── DakDetailScreen
│   ├── VloerDetailScreen
│   └── InstallatieScreen
├── CalendarStack
│   └── CalendarScreen (Visit Schedule)
├── MeasureStack
│   ├── MeasurementScreen (Live Dashboard)
│   └── PhotoCaptureScreen
├── DevicesStack
│   ├── DeviceManagerScreen (BLE Pairing)
│   └── DeviceDetailScreen
└── SettingsStack
    ├── SettingsScreen
    ├── SyncScreen (Offline Status)
    └── ReportScreen
```

---

## 2. Key Dependencies

```json
{
  "dependencies": {
    "@supabase/supabase-js": "^2.39.0",
    "@react-navigation/native": "^6.1.0",
    "@react-navigation/bottom-tabs": "^6.5.0",
    "@react-navigation/stack": "^6.3.0",
    "react-native-ble-plx": "^3.1.0",
    "zustand": "^4.5.0",
    "react-native-mmkv": "^2.11.0",
    "@shopify/react-native-skia": "^0.1.0",
    "react-native-reanimated": "^3.6.0",
    "expo-camera": "~14.0.0",
    "expo-location": "~16.5.0",
    "expo-file-system": "~16.0.0",
    "date-fns": "^3.3.0",
    "zod": "^3.22.0"
  }
}
```

---

## 3. Core Screens

### MeasurementInput Component (BLE-Linked Field)

```typescript
// src/components/forms/MeasurementInput.tsx
import React, { useState, useCallback } from 'react';
import { View, Text, TextInput, TouchableOpacity, Animated } from 'react-native';
import { useBLEStore } from '../../store/bleStore';

interface Props {
  label: string;
  unit: 'mm' | 'cm' | 'm';
  value: number | null;
  onChange: (value: number) => void;
  elementId: string;
}

export function MeasurementInput({ label, unit, value, onChange, elementId }: Props) {
  const [listening, setListening] = useState(false);
  const { latestMeasurement, isConnected } = useBLEStore();
  const pulseAnim = new Animated.Value(1);

  const startCapture = useCallback(() => {
    setListening(true);
    // Pulse animation while waiting for BLE measurement
    Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, { toValue: 1.2, duration: 500, useNativeDriver: true }),
        Animated.timing(pulseAnim, { toValue: 1, duration: 500, useNativeDriver: true }),
      ])
    ).start();
  }, []);

  // When BLE measurement arrives while listening
  React.useEffect(() => {
    if (listening && latestMeasurement) {
      const converted = convertUnit(latestMeasurement.value_mm, unit);
      onChange(converted);
      setListening(false);
      pulseAnim.stopAnimation();
    }
  }, [latestMeasurement, listening]);

  return (
    <View style={styles.container}>
      <Text style={styles.label}>{label}</Text>
      <View style={styles.inputRow}>
        <TextInput
          style={styles.input}
          value={value?.toString() || ''}
          onChangeText={t => onChange(parseFloat(t))}
          keyboardType="decimal-pad"
          placeholder={`Enter ${label.toLowerCase()}`}
        />
        <Text style={styles.unit}>{unit}</Text>
        <TouchableOpacity
          onPress={startCapture}
          disabled={!isConnected}
          style={[styles.bleButton, listening && styles.bleButtonActive]}
        >
          <Animated.View style={{ transform: [{ scale: pulseAnim }] }}>
            <Text style={styles.bleIcon}>📡</Text>
          </Animated.View>
        </TouchableOpacity>
      </View>
      {listening && <Text style={styles.hint}>Take measurement on GLM device...</Text>}
    </View>
  );
}
```

### Offline Sync Service

```typescript
// src/services/syncService.ts
import { MMKV } from 'react-native-mmkv';
import { supabase } from './supabaseClient';

const storage = new MMKV();
const QUEUE_KEY = 'sync_queue';

interface SyncMutation {
  id: string;
  table: string;
  operation: 'INSERT' | 'UPDATE' | 'DELETE';
  data: Record<string, any>;
  timestamp: string;
  synced: boolean;
}

export const syncService = {
  enqueue(mutation: Omit<SyncMutation, 'id' | 'synced'>) {
    const queue = this.getQueue();
    queue.push({ ...mutation, id: crypto.randomUUID(), synced: false });
    storage.set(QUEUE_KEY, JSON.stringify(queue));
  },

  getQueue(): SyncMutation[] {
    const raw = storage.getString(QUEUE_KEY);
    return raw ? JSON.parse(raw) : [];
  },

  async syncAll(): Promise<{ synced: number; failed: number }> {
    const queue = this.getQueue().filter(m => !m.synced);
    let synced = 0, failed = 0;

    for (const mutation of queue) {
      try {
        if (mutation.operation === 'INSERT') {
          await supabase.from(mutation.table).insert(mutation.data);
        } else if (mutation.operation === 'UPDATE') {
          await supabase.from(mutation.table).update(mutation.data).eq('id', mutation.data.id);
        } else if (mutation.operation === 'DELETE') {
          await supabase.from(mutation.table).delete().eq('id', mutation.data.id);
        }
        mutation.synced = true;
        synced++;
      } catch (err) {
        failed++;
      }
    }

    storage.set(QUEUE_KEY, JSON.stringify(queue));
    return { synced, failed };
  },

  getPendingCount(): number {
    return this.getQueue().filter(m => !m.synced).length;
  }
};
```

---

## 4. EAS Build Configuration

```json
// eas.json
{
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "ios": { "simulator": true },
      "env": { "EXPO_PUBLIC_SUPABASE_URL": "http://localhost:3001" }
    },
    "preview": {
      "distribution": "internal",
      "env": { "EXPO_PUBLIC_SUPABASE_URL": "https://staging.scarnergy.krontiva.com" }
    },
    "production": {
      "env": { "EXPO_PUBLIC_SUPABASE_URL": "https://api.scarnergy.krontiva.com" }
    }
  }
}
```

---

## 5. iOS and Android Specifics

### iOS BLE Permissions (Info.plist via app.json)
```json
{
  "expo": {
    "ios": {
      "infoPlist": {
        "NSBluetoothAlwaysUsageDescription": "Connect to Bosch GLM laser rangefinder for measurements",
        "NSBluetoothPeripheralUsageDescription": "Communicate with Bosch GLM laser rangefinder",
        "UIBackgroundModes": ["bluetooth-central"]
      }
    },
    "android": {
      "permissions": [
        "BLUETOOTH", "BLUETOOTH_ADMIN", "BLUETOOTH_CONNECT",
        "BLUETOOTH_SCAN", "ACCESS_FINE_LOCATION", "CAMERA"
      ]
    }
  }
}
```

---

*This document is confidential and intended for Krontiva Africa internal use only.*
