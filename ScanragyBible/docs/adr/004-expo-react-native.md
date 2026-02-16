# ADR-004: Expo / React Native for Mobile (iOS + Android)

**Status**: Accepted  
**Date**: 2026-02-11

## Context
Scarnergy requires native mobile apps for iOS and Android with BLE connectivity to Bosch GLM devices. The existing prototype uses Expo with sample data.

## Decision
Continue with **React Native via Expo** with EAS Build for native BLE support.

## Rationale
- Existing codebase continuity (Expo app already built)
- Cross-platform: single codebase for iOS and Android
- EAS Build enables native modules (react-native-ble-plx) via dev client
- react-native-ble-plx is the most mature BLE library for React Native
- Zustand + MMKV provides offline-first state management
- Active ecosystem with extensive community support

## Trade-offs
- BLE requires Expo Dev Client (not Expo Go)
- iOS BLE permissions require careful handling
- Performance-critical charts use react-native-skia instead of web-based charting
