# Scarnergy — Energy Calculations Engine

> **Standard**: NTA 8800 (Dutch energy performance methodology)  
> **Implementation**: Supabase Edge Function + client-side TypeScript  
> **Output**: Energy label (A–G) with detailed breakdown

---

## 1. NTA 8800 Simplified Calculation Flow

```
Building Envelope           →    Transmission Loss    →    Energy Demand    →    Label
(Gevels + Daken + Vloeren)       (U-values × areas)       (losses / efficiency)
     │                                │                         │
     ├─ Facade areas (net)           ├─ Wall U-value            ├─ Heating demand
     ├─ Roof areas (net)             ├─ Roof U-value            ├─ System efficiency
     ├─ Floor areas                  ├─ Floor U-value           ├─ Ventilation loss
     ├─ Opening areas                ├─ Window U-value          ├─ Solar gains
     └─ Insulation properties        └─ Thermal bridges         └─ Energy Index
```

## 2. Energy Label Scale

| Label | Energy Index Range | Description |
|-------|-------------------|-------------|
| A++++ | ≤ 0.00 | Net-zero or energy-positive |
| A+++ | 0.01 – 0.20 | Nearly zero-energy building |
| A++ | 0.21 – 0.40 | Very energy efficient |
| A+ | 0.41 – 0.60 | Energy efficient |
| A | 0.61 – 0.80 | Good |
| B | 0.81 – 1.20 | Above average |
| C | 1.21 – 1.40 | Average |
| D | 1.41 – 1.80 | Below average |
| E | 1.81 – 2.10 | Poor |
| F | 2.11 – 2.40 | Very poor |
| G | > 2.40 | Worst |

---

## 3. Key Formulas

```typescript
// Transmission loss through building envelope
function calculateTransmissionLoss(gevels, daken, vloeren, openings) {
  const wallLoss = gevels.reduce((sum, g) =>
    sum + (g.netto_oppervlakte / 1e6) * getUValue('wall', g), 0);
  const roofLoss = daken.reduce((sum, d) =>
    sum + (d.netto_oppervlakte / 1e6) * getUValue('roof', d), 0);
  const floorLoss = vloeren.reduce((sum, v) =>
    sum + (v.oppervlakte / 1e6) * getUValue('floor', v), 0);
  const windowLoss = openings.reduce((sum, o) =>
    sum + (o.bruto_oppervlakte / 1e6) * getUValue('window', o), 0);
  return (wallLoss + roofLoss + floorLoss + windowLoss) * DEGREE_DAYS * 24 / 1000;
}

// Energy Index calculation
function calculateEnergyIndex(object, zones, elements, installations) {
  const transmissionLoss = calculateTransmissionLoss(...);
  const ventilationLoss = calculateVentilationLoss(object);
  const totalDemand = transmissionLoss + ventilationLoss;
  const systemEfficiency = calculateSystemEfficiency(installations);
  const totalFloorArea = zones.reduce((s, z) => s + z.oppervlakte, 0);
  return totalDemand / (totalFloorArea * systemEfficiency);
}
```

---

*This document is confidential and intended for Krontiva Africa internal use only.*
