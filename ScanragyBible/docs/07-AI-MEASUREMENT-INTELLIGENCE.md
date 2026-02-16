# Scarnergy — AI Measurement Intelligence

> **Role**: Validate measurements, detect anomalies, classify measurement types, predict energy performance  
> **Server**: FastAPI inference server (scikit-learn)  
> **Mobile**: TFLite on-device models (<2MB each)  
> **Novel**: Real-time AI feedback during field measurement capture

---

## 1. AI Pipeline Architecture

```
CAPTURE                    VALIDATE (On-Device)            VALIDATE (Server)           ANALYZE
──────────────            ──────────────────────          ──────────────────          ──────────
BLE Measurement  ──────►  TFLite Anomaly Detector  ────►  FastAPI Batch Validate ──►  Metabase
  │                         │                                │                         Dashboard
  │                         ├─ Score: 0.0–1.0               ├─ Geometry cross-check
  │                         ├─ Green/Yellow/Red              ├─ Session consistency
  │                         └─ <50ms on mobile               └─ Building standards check
  │
  │                       TFLite Classifier  ─────────────►  Auto-assign measurement
  │                         ├─ height / width / depth         to correct element field
  │                         ├─ diagonal / perimeter
  │                         └─ <30ms on mobile
```

---

## 2. Model 1: Anomaly Detector (Isolation Forest)

### Training Data Generation

```python
# services/ai-engine/data/synthetic_measurements.py
import numpy as np
import pandas as pd

def generate_training_data(n_samples=50000, anomaly_ratio=0.05):
    n_normal = int(n_samples * (1 - anomaly_ratio))
    n_anomaly = n_samples - n_normal

    # Normal measurements (Dutch residential buildings)
    normal = pd.DataFrame({
        'value_mm': np.concatenate([
            np.random.normal(2700, 400, n_normal // 4),    # Wall heights
            np.random.normal(4500, 1500, n_normal // 4),   # Wall widths
            np.random.normal(5000, 2000, n_normal // 4),   # Roof dimensions
            np.random.normal(3000, 1000, n_normal // 4),   # Floor dimensions
        ]),
        'measurement_rate': np.random.exponential(2, n_normal),
        'time_since_last': np.random.exponential(5, n_normal),
        'element_type': np.random.choice(['gevel', 'dak', 'vloer', 'opening'], n_normal),
        'session_mean': np.random.normal(3500, 1000, n_normal),
        'session_std': np.random.exponential(500, n_normal),
        'is_anomaly': 0
    })

    # Anomalous measurements
    anomalies = pd.DataFrame({
        'value_mm': np.concatenate([
            np.random.uniform(-1000, 49, n_anomaly // 4),        # Negative/too small
            np.random.uniform(50001, 100000, n_anomaly // 4),    # Too large
            np.repeat(2700.0, n_anomaly // 4),                    # Stuck sensor
            np.random.uniform(30000, 50000, n_anomaly // 4),     # Unrealistic for residential
        ]),
        'measurement_rate': np.random.uniform(5, 20, n_anomaly),
        'time_since_last': np.random.uniform(0, 0.3, n_anomaly),
        'element_type': np.random.choice(['gevel', 'dak', 'vloer', 'opening'], n_anomaly),
        'session_mean': np.random.normal(3500, 1000, n_anomaly),
        'session_std': np.random.exponential(500, n_anomaly),
        'is_anomaly': 1
    })

    return pd.concat([normal, anomalies]).sample(frac=1).reset_index(drop=True)
```

### Model Training

```python
# services/ai-engine/training/train_anomaly_model.py
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import cross_val_score
import joblib

def train_anomaly_model(df):
    features = ['value_mm', 'measurement_rate', 'time_since_last',
                'session_mean', 'session_std']

    le = LabelEncoder()
    df['element_type_enc'] = le.fit_transform(df['element_type'])
    features.append('element_type_enc')

    scaler = StandardScaler()
    X = scaler.fit_transform(df[features])

    model = IsolationForest(
        n_estimators=200,
        contamination=0.05,
        max_samples='auto',
        random_state=42
    )
    model.fit(X[df['is_anomaly'] == 0])  # Train on normal data only

    # Evaluate
    scores = model.decision_function(X)
    predictions = model.predict(X)  # 1 = normal, -1 = anomaly

    # Export
    joblib.dump({'model': model, 'scaler': scaler, 'encoder': le}, 'anomaly_detector.joblib')
    return model, scaler, le
```

### TFLite Conversion for Mobile

```python
# services/ai-engine/inference/tflite_converter.py
import tensorflow as tf
import numpy as np

def convert_to_tflite(joblib_path, output_path):
    """Convert sklearn model to TFLite via TF wrapper."""
    artifacts = joblib.load(joblib_path)
    model = artifacts['model']
    scaler = artifacts['scaler']

    # Create a TF model that wraps the sklearn prediction
    class AnomalyModel(tf.Module):
        def __init__(self):
            super().__init__()
            self.threshold = tf.constant(model.offset_, dtype=tf.float32)
            # Store tree parameters as TF constants
            # (simplified — full implementation uses ONNX intermediate)

        @tf.function(input_signature=[tf.TensorSpec(shape=[1, 6], dtype=tf.float32)])
        def predict(self, x):
            # Anomaly score computation
            score = self._compute_score(x)
            return score

    # Alternative: Use ONNX → TFLite conversion pipeline
    # pip install skl2onnx onnx2tf
    from skl2onnx import convert_sklearn
    from skl2onnx.common.data_types import FloatTensorType

    initial_type = [('float_input', FloatTensorType([None, 6]))]
    onnx_model = convert_sklearn(model, initial_types=initial_type)

    # ONNX → TFLite
    import onnx2tf
    onnx2tf.convert(onnx_model, output_path, output_signaturedefs=True)
```

---

## 3. Model 2: Measurement Type Classifier

Classifies what a measurement likely represents based on value range and session context.

| Class | Typical Range (mm) | Context |
|-------|-------------------|---------|
| `wall_height` | 2400–4000 | First measurement in gevel context |
| `wall_width` | 1500–15000 | Second measurement in gevel context |
| `roof_length` | 3000–15000 | In dak context |
| `roof_slope_run` | 1000–8000 | Horizontal component of roof |
| `opening_height` | 400–3000 | In transparant deel context |
| `opening_width` | 400–3000 | In transparant deel context |
| `floor_length` | 2000–15000 | In vloer context |
| `floor_width` | 2000–10000 | In vloer context |
| `depth` | 100–500 | Insulation/wall thickness |

---

## 4. FastAPI Inference Server

```python
# services/ai-engine/inference/server.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib

app = FastAPI(title="Scarnergy AI Engine", version="2.0")

# Load models at startup
anomaly_model = joblib.load("models/anomaly_detector.joblib")
classifier_model = joblib.load("models/measurement_classifier.joblib")

class MeasurementInput(BaseModel):
    value_mm: float
    measurement_rate: float = 1.0
    time_since_last: float = 5.0
    element_type: str = "gevel"
    session_mean: float = 3500.0
    session_std: float = 500.0

class ValidationResult(BaseModel):
    is_anomaly: bool
    anomaly_score: float
    measurement_type: str
    confidence: float
    flags: list[str]

@app.post("/validate", response_model=ValidationResult)
def validate_measurement(m: MeasurementInput):
    features = preprocess(m)
    anomaly_score = float(anomaly_model['model'].decision_function(features)[0])
    is_anomaly = anomaly_score < 0
    measurement_type, confidence = classify(m)

    flags = []
    if m.value_mm < 50: flags.append("BELOW_MIN_RANGE")
    if m.value_mm > 50000: flags.append("ABOVE_MAX_RANGE")
    if is_anomaly: flags.append("ANOMALY_DETECTED")

    return ValidationResult(
        is_anomaly=is_anomaly,
        anomaly_score=anomaly_score,
        measurement_type=measurement_type,
        confidence=confidence,
        flags=flags
    )

@app.get("/health")
def health(): return {"status": "healthy", "models_loaded": True}
```

---

## 5. Mobile Integration

```typescript
// mobile/inspector-app/src/hooks/useAnomalyDetection.ts
import { useState, useCallback } from 'react';

export function useAnomalyDetection() {
  const [loading, setLoading] = useState(false);

  const validate = useCallback(async (measurement: {
    value_mm: number;
    element_type: string;
    session_stats: { mean: number; std: number };
  }) => {
    // On-device validation (TFLite) — instant feedback
    const localScore = runTFLiteModel(measurement);

    // Server-side validation (if online) — comprehensive check
    let serverResult = null;
    try {
      const res = await fetch(`${AI_ENGINE_URL}/validate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(measurement),
      });
      serverResult = await res.json();
    } catch { /* offline — use local result only */ }

    return {
      isAnomaly: localScore < 0 || serverResult?.is_anomaly,
      score: serverResult?.anomaly_score ?? localScore,
      type: serverResult?.measurement_type ?? 'unknown',
      flags: serverResult?.flags ?? [],
    };
  }, []);

  return { validate, loading };
}
```

---

*This document is confidential and intended for Krontiva Africa internal use only.*
