# Considition 2025 Data Structures - ANALYZED

## Overview
This is an **EV Charging Recommendation System**. Customers are car/truck owners who need advice on when and where to charge their vehicles during their journeys.

## Map Object Structure (CONFIRMED)

```json
{
  "name": "Turbohill",
  "dimX": 10,
  "dimY": 10,
  "ticks": 288,
  "nodes": [...],
  "edges": [...],
  "zones": [...]
}
```

### Node Structure
```json
{
  "id": "0.0",
  "posX": 0,
  "posY": 0,
  "zoneId": "0.0<-->4.4",
  "customers": [...],
  "target": {
    "Type": "ChargingStation" | "Null",
    "amountOfAvailableChargers": 3,
    "totalAmountOfBrokenChargers": 2,
    "chargeSpeedPerCharger": 199,
    "totalAmountOfChargers": 5
  }
}
```

### Customer Structure
```json
{
  "id": "0.2",
  "type": "Car" | "Truck",
  "persona": "CostSensitive" | "Stressed" | "DislikesDriving" | "EcoConscious" | "Neutral",
  "fromNode": "0.0",
  "toNode": "0.3",
  "departureTick": 40,
  "chargeRemaining": 0.27612832,  // Fraction (0-1)
  "maxCharge": 50,  // kWh
  "energyConsumptionPerKm": 0.2,  // Car: 0.2, Truck: 1.0
  "state": "Home"
}
```

### Edge Structure
```json
{
  "id": "0.0-->0.1",
  "fromNode": "0.0",
  "toNode": "0.1",
  "length": 35.20188,  // Distance in km
  "customers": []
}
```

### Zone Structure
```json
{
  "id": "0.0<-->4.4",
  "topLeftX": 0,
  "topLeftY": 0,
  "bottomRightX": 4,
  "bottomRightY": 4,
  "energySources": [
    {
      "type": "Nuclear" | "Hydro" | "Coal" | "NaturalGas" | "Wind" | "Solar",
      "generationCapacity": 0.5
    }
  ],
  "energyStorages": [
    {
      "capacityMWh": 500,
      "efficiency": 0.85,
      "maxChargePowerMw": 50,
      "maxDischargePowerMw": 50
    }
  ]
}
```

## Customer Recommendation Format (NEEDS CONFIRMATION)

Based on analysis, we're implementing:

```json
{
  "customerId": "0.2",
  "chargingStation": "1.1",
  "chargeAmount": 15.5,
  "route": ["0.0", "1.1", "0.3"]
}
```

### Questions Still Needed:
1. **What is the exact expected format for recommendations?**
   - Do we need to specify charging duration?
   - Is the route optional or required?
   - What other fields are expected?

2. **What happens in the game response?**
   - How does the state update after a tick?
   - Are customers removed after recommendations?
   - How do we track charging progress?

3. **Scoring System:**
   - How are points calculated?
   - Penalties for bad recommendations?
   - Bonuses for green energy usage?

## Key Insights

### Energy Sources (Green vs Dirty)
- **Green:** Nuclear, Hydro, Wind, Solar
- **Dirty:** Coal, NaturalGas

### Customer Personas
- **Stressed:** Minimize time, prefer fast charging, avoid detours
- **DislikesDriving:** Similar to Stressed
- **CostSensitive:** Prefer cheaper options (green energy zones)
- **EcoConscious:** Strongly prefer green energy stations
- **Neutral:** Balanced approach

### Vehicle Types
- **Car:** 0.2 kWh/km consumption
- **Truck:** 1.0 kWh/km consumption (5x more)

## Current Algorithm Implementation

The algorithm now:
1. ✅ Parses map structure correctly
2. ✅ Builds graph for pathfinding
3. ✅ Identifies charging stations
4. ✅ Implements Dijkstra's shortest path
5. ✅ Calculates energy requirements
6. ✅ Scores stations based on persona
7. ✅ Generates charging recommendations

### What We Need to Test:
1. Run the simulation once to see if the recommendation format is correct
2. Check the game response to understand state updates
3. Adjust algorithm based on actual game behavior
4. Optimize scoring function based on results

## Next Steps

1. **Test the current implementation**
   ```bash
   export API_KEY=your_key
   python app.py
   ```

2. **Check for errors** and adjust recommendation format

3. **Analyze game response** to understand:
   - How recommendations are processed
   - How customer states update
   - What the scoring mechanism is

4. **Iterate on the algorithm** based on results
