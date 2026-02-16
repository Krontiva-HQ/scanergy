# ADR-005: TensorFlow Lite for On-Device Measurement AI

**Status**: Accepted  
**Date**: 2026-02-11

## Context
Measurements need real-time validation feedback — inspectors should know immediately if a measurement is anomalous. Server-side validation introduces latency and requires network connectivity.

## Decision
Deploy **TensorFlow Lite** models on mobile devices for instant measurement validation, complemented by server-side FastAPI inference for comprehensive checks.

## Rationale
- <50ms inference on mobile (vs 200ms+ for server round-trip)
- Works offline — critical for field inspections without connectivity
- Models are small (<2MB each) and can be bundled with the app
- scikit-learn → ONNX → TFLite conversion pipeline is well-established
- Server-side FastAPI provides comprehensive validation when online
- Dual validation (local + server) provides defense-in-depth

## Models
1. **Anomaly Detector** (Isolation Forest → TFLite): Flags physically impossible measurements
2. **Measurement Classifier** (Random Forest → TFLite): Suggests measurement type (height/width/depth)
